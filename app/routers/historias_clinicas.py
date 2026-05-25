from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.core.security import get_current_user  # 👈 Importamos la seguridad
from app.models.user import User
from app.models.historia_clinica import HistoriaClinica
from app.models.paciente import Paciente
from app.models.kinesiologo import Kinesiologo
from app.schemas.historia_clinica_schema import (
    HistoriaClinicaCreate,
    HistoriaClinicaUpdate,
    HistoriaClinicaOut
)

router = APIRouter(prefix="/historias-clinicas", tags=["Historias Clínicas"])

# 🛡️ HELPER DE PERMISOS
def verificar_rol_profesional(current_user: User):
    """Lanza error si el usuario no es admin ni kinesiólogo"""
    roles = [r.name for r in current_user.roles]
    if "admin" not in roles and "kinesiologo" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a historias clínicas."
        )

# ==========================================
# LISTAR TODAS (Solo Admin y Kinesiólogos)
# ==========================================
@router.get("/", response_model=List[HistoriaClinicaOut])
def listar_historias(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # 🔒 Auth requerida
):
    # 1. Validar permiso (Recepcionistas y Pacientes NO pueden ver el listado global)
    verificar_rol_profesional(current_user)

    historias = (
        db.query(HistoriaClinica)
        .options(
            joinedload(HistoriaClinica.paciente).joinedload(Paciente.user),
            joinedload(HistoriaClinica.kinesiologo).joinedload(Kinesiologo.user)
        )
        .order_by(HistoriaClinica.fecha_consulta.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return historias


# ==========================================
# OBTENER HISTORIAS DE UN PACIENTE
# ==========================================
@router.get("/paciente/{paciente_id}", response_model=List[HistoriaClinicaOut])
def obtener_historias_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # 🔒 Auth requerida
):
    roles = [r.name for r in current_user.roles]

    # 1. Si es Paciente, SOLO puede ver las suyas
    if "paciente" in roles and "admin" not in roles and "kinesiologo" not in roles:
        # Verificar si el ID solicitado coincide con su perfil de paciente
        if not current_user.paciente or current_user.paciente.id != paciente_id:
            raise HTTPException(
                status_code=403, 
                detail="No tienes permiso para ver la historia clínica de otro paciente."
            )

    # 2. Si es Recepcionista (y no tiene otro rol superior), bloqueado
    if "recepcionista" in roles and "admin" not in roles and "kinesiologo" not in roles:
         raise HTTPException(status_code=403, detail="Confidencialidad médica: Acceso denegado.")

    # Verificar que el paciente existe
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    historias = (
        db.query(HistoriaClinica)
        .options(
            joinedload(HistoriaClinica.kinesiologo).joinedload(Kinesiologo.user)
        )
        .filter(HistoriaClinica.paciente_id == paciente_id)
        .order_by(HistoriaClinica.fecha_consulta.desc())
        .all()
    )
    
    return historias


# ==========================================
# OBTENER UNA HISTORIA POR ID
# ==========================================
@router.get("/{historia_id}", response_model=HistoriaClinicaOut)
def obtener_historia(
    historia_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    historia = (
        db.query(HistoriaClinica)
        .options(
            joinedload(HistoriaClinica.paciente).joinedload(Paciente.user),
            joinedload(HistoriaClinica.kinesiologo).joinedload(Kinesiologo.user)
        )
        .filter(HistoriaClinica.id == historia_id)
        .first()
    )
    
    if not historia:
        raise HTTPException(status_code=404, detail="Historia clínica no encontrada")

    # VALIDACIÓN DE SEGURIDAD
    roles = [r.name for r in current_user.roles]
    
    # Si es paciente, solo puede ver si le pertenece
    if "paciente" in roles and "kinesiologo" not in roles and "admin" not in roles:
        if not current_user.paciente or current_user.paciente.id != historia.paciente_id:
            raise HTTPException(status_code=403, detail="Acceso denegado.")
            
    # Si es recepcionista puro, denegado
    if "recepcionista" in roles and "kinesiologo" not in roles and "admin" not in roles:
        raise HTTPException(status_code=403, detail="Acceso denegado.")
    
    return historia


# ==========================================
# CREAR (Solo Kinesiólogos y Admin)
# ==========================================
@router.post("/", response_model=HistoriaClinicaOut, status_code=201)
def crear_historia(
    historia_data: HistoriaClinicaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 🔒 Solo profesionales pueden escribir
    verificar_rol_profesional(current_user)

    # Validaciones de existencia
    paciente = db.query(Paciente).filter(Paciente.id == historia_data.paciente_id).first()
    if not paciente: raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    kinesiologo = db.query(Kinesiologo).filter(Kinesiologo.id == historia_data.kinesiologo_id).first()
    if not kinesiologo: raise HTTPException(status_code=404, detail="Kinesiólogo no encontrado")
    
    nueva_historia = HistoriaClinica(**historia_data.model_dump())
    db.add(nueva_historia)
    db.commit()
    db.refresh(nueva_historia)
    
    return db.query(HistoriaClinica).options(
        joinedload(HistoriaClinica.paciente).joinedload(Paciente.user),
        joinedload(HistoriaClinica.kinesiologo).joinedload(Kinesiologo.user)
    ).filter(HistoriaClinica.id == nueva_historia.id).first()


# ==========================================
# ACTUALIZAR (Solo Kinesiólogos y Admin)
# ==========================================
@router.put("/{historia_id}", response_model=HistoriaClinicaOut)
def actualizar_historia(
    historia_id: int,
    historia_data: HistoriaClinicaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 🔒 Seguridad
    verificar_rol_profesional(current_user)

    historia = db.query(HistoriaClinica).filter(HistoriaClinica.id == historia_id).first()
    if not historia: raise HTTPException(status_code=404, detail="Historia no encontrada")
    
    for field, value in historia_data.model_dump(exclude_unset=True).items():
        setattr(historia, field, value)
    
    db.commit()
    db.refresh(historia)
    
    return db.query(HistoriaClinica).options(
        joinedload(HistoriaClinica.paciente).joinedload(Paciente.user),
        joinedload(HistoriaClinica.kinesiologo).joinedload(Kinesiologo.user)
    ).filter(HistoriaClinica.id == historia_id).first()


# ==========================================
# ELIMINAR (Solo Admin)
# ==========================================
@router.delete("/{historia_id}", status_code=204)
def eliminar_historia(
    historia_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 🔒 ULTRA Seguridad: Solo Admin puede borrar historias clínicas (Auditoría)
    roles = [r.name for r in current_user.roles]
    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="Solo un administrador puede eliminar historias clínicas.")

    historia = db.query(HistoriaClinica).filter(HistoriaClinica.id == historia_id).first()
    if not historia: raise HTTPException(status_code=404, detail="Historia no encontrada")
    
    db.delete(historia)
    db.commit()
    return None

# ==========================================
# ESTADÍSTICAS (Solo Profesionales)
# ==========================================
@router.get("/paciente/{paciente_id}/estadisticas")
def obtener_estadisticas_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Permitimos al paciente ver sus propias estadísticas
    roles = [r.name for r in current_user.roles]
    if "paciente" in roles and "kinesiologo" not in roles and "admin" not in roles:
        if not current_user.paciente or current_user.paciente.id != paciente_id:
            raise HTTPException(status_code=403, detail="Acceso denegado")
            
    # Recepcionistas fuera
    if "recepcionista" in roles and "kinesiologo" not in roles and "admin" not in roles:
         raise HTTPException(status_code=403, detail="Acceso denegado")

    historias = db.query(HistoriaClinica)\
        .filter(HistoriaClinica.paciente_id == paciente_id)\
        .order_by(HistoriaClinica.fecha_consulta.desc()).all()
    
    if not historias:
        return {"total_consultas": 0, "ultima_consulta": None}
    
    return {
        "total_consultas": len(historias),
        "ultima_consulta": historias[0].fecha_consulta,
        "primera_consulta": historias[-1].fecha_consulta,
        "peso_actual": historias[0].peso,
        "presion_actual": historias[0].presion_arterial
    }