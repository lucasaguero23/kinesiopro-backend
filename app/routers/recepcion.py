from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from datetime import date, datetime, time
from typing import List, Optional

from app.database import get_db
from app.core.permissions import role_required
from app.core.token import get_current_user

# Modelos
from app.models.turno import Turno
from app.models.paciente import Paciente
from app.models.kinesiologo import Kinesiologo
from app.models.user import User

# Schemas
from app.schemas.turno_schema import TurnoOut


router = APIRouter(
    prefix="/recepcion",
    tags=["Recepción"]
)


# ─────────────────────────────────────────────
# 📅 Turnos del día actual
# ─────────────────────────────────────────────
@router.get("/turnos-hoy", response_model=List[TurnoOut])
def turnos_de_hoy(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required("recepcionista", "admin"))
):
    """
    Obtener todos los turnos del día actual.
    Solo accesible por recepcionistas y admins.
    """
    hoy = date.today()
    
    turnos = (
        db.query(Turno)
        .options(
            joinedload(Turno.paciente).joinedload(Paciente.user),
            joinedload(Turno.kinesiologo).joinedload(Kinesiologo.user),
            joinedload(Turno.servicio),
            joinedload(Turno.sala)
        )
        .filter(Turno.fecha == hoy)
        .order_by(Turno.hora_inicio.asc())
        .all()
    )
    
    return turnos


# ─────────────────────────────────────────────
# 📅 Turnos por rango de fechas
# ─────────────────────────────────────────────
@router.get("/turnos", response_model=List[TurnoOut])
def turnos_recepcion(
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    estado: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required("recepcionista", "admin"))
):
    """
    Obtener turnos con filtros opcionales.
    Solo accesible por recepcionistas y admins.
    """
    query = db.query(Turno).options(
        joinedload(Turno.paciente).joinedload(Paciente.user),
        joinedload(Turno.kinesiologo).joinedload(Kinesiologo.user),
        joinedload(Turno.servicio),
        joinedload(Turno.sala)
    )
    
    # Aplicar filtros
    if fecha_desde:
        query = query.filter(Turno.fecha >= fecha_desde)
    if fecha_hasta:
        query = query.filter(Turno.fecha <= fecha_hasta)
    if estado:
        query = query.filter(Turno.estado == estado)
    
    # Si no hay filtros, mostrar turnos de hoy
    if not fecha_desde and not fecha_hasta:
        query = query.filter(Turno.fecha == date.today())
    
    return query.order_by(Turno.fecha.asc(), Turno.hora_inicio.asc()).all()


# ─────────────────────────────────────────────
# ✅ Confirmar asistencia de paciente
# ─────────────────────────────────────────────
@router.patch("/{turno_id}/confirmar-asistencia")
def confirmar_asistencia(
    turno_id: int,
    llego_tarde: bool = Query(False, description="Indica si el paciente llegó tarde"),
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required("recepcionista", "admin"))
):
    """
    Confirmar que el paciente asistió al turno.
    Opcionalmente marcar si llegó tarde.
    """
    turno = db.query(Turno).filter(Turno.id == turno_id).first()
    
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    
    # Cambiar estado a confirmado
    turno.estado = "confirmado"
    
    # Agregar observación si llegó tarde
    if llego_tarde:
        observacion_tarde = f"Paciente llegó tarde - Registrado por {current_user.nombre} a las {datetime.now().strftime('%H:%M')}"
        if turno.observaciones:
            turno.observaciones += f"\n{observacion_tarde}"
        else:
            turno.observaciones = observacion_tarde
    
    db.commit()
    db.refresh(turno)
    
    return {
        "message": "Asistencia confirmada correctamente",
        "turno_id": turno_id,
        "llego_tarde": llego_tarde,
        "estado": turno.estado
    }


# ─────────────────────────────────────────────
# ❌ Marcar como ausente (no asistió)
# ─────────────────────────────────────────────
@router.patch("/{turno_id}/marcar-ausente")
def marcar_ausente(
    turno_id: int,
    motivo: Optional[str] = Query(None, description="Motivo de la ausencia"),
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required("recepcionista", "admin"))
):
    """
    Marcar que el paciente no asistió al turno.
    """
    turno = db.query(Turno).filter(Turno.id == turno_id).first()
    
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    
    # Cambiar estado a cancelado
    turno.estado = "cancelado"
    
    # Agregar observación
    observacion = f"Paciente ausente - Registrado por {current_user.nombre} a las {datetime.now().strftime('%H:%M')}"
    if motivo:
        observacion += f" - Motivo: {motivo}"
    
    if turno.observaciones:
        turno.observaciones += f"\n{observacion}"
    else:
        turno.observaciones = observacion
    
    db.commit()
    db.refresh(turno)
    
    return {
        "message": "Turno marcado como ausente",
        "turno_id": turno_id,
        "estado": turno.estado
    }


# ─────────────────────────────────────────────
# 📊 Estadísticas del día
# ─────────────────────────────────────────────
@router.get("/estadisticas-hoy")
def estadisticas_hoy(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required("recepcionista", "admin"))
):
    """
    Obtener estadísticas de turnos del día actual.
    """
    hoy = date.today()
    
    turnos_hoy = db.query(Turno).filter(Turno.fecha == hoy).all()
    
    total = len(turnos_hoy)
    pendientes = len([t for t in turnos_hoy if t.estado == "pendiente"])
    confirmados = len([t for t in turnos_hoy if t.estado == "confirmado"])
    cancelados = len([t for t in turnos_hoy if t.estado == "cancelado"])
    completados = len([t for t in turnos_hoy if t.estado == "completado"])
    
    return {
        "fecha": hoy,
        "total_turnos": total,
        "pendientes": pendientes,
        "confirmados": confirmados,
        "cancelados": cancelados,
        "completados": completados
    }


# ─────────────────────────────────────────────
# 🔍 Buscar paciente por DNI o nombre
# ─────────────────────────────────────────────
@router.get("/buscar-paciente")
def buscar_paciente(
    query: str = Query(..., min_length=2, description="DNI o nombre del paciente"),
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required("recepcionista", "admin"))
):
    """
    Buscar pacientes por DNI o nombre.
    """
    pacientes = (
        db.query(Paciente)
        .join(User)
        .filter(
            (Paciente.dni.ilike(f"%{query}%")) | 
            (User.nombre.ilike(f"%{query}%"))
        )
        .options(joinedload(Paciente.user))
        .limit(10)
        .all()
    )
    
    resultados = [
        {
            "id": p.id,
            "nombre": p.user.nombre if p.user else "Sin nombre",
            "email": p.user.email if p.user else "Sin email",
            "dni": p.dni,
            "telefono": p.telefono,
            "obra_social": p.obra_social
        }
        for p in pacientes
    ]
    
    return {
        "query": query,
        "resultados": resultados,
        "total": len(resultados)
    }
