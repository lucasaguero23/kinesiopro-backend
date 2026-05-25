from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from app.database import get_db
from app.core.crud import kinesiologo_crud
from app.schemas.kinesiologo_schema import KinesiologoCreate, KinesiologoUpdate, KinesiologoOut
from app.core.validaciones import validar_email_formato, MensajesError, capitalizar_texto
from app.models.user import User
from app.models.kinesiologo import Kinesiologo
from app.models.turno import Turno
from app.models.role import Role
from app.models.user_role import UserRole
from app.core.security import get_password_hash

router = APIRouter(
    prefix="/kinesiologos",
    tags=["Kinesiologos"]
)

# ═══════════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES DE VALIDACIÓN
# ═══════════════════════════════════════════════════════════════════════════

def verificar_matricula_existente(db: Session, matricula: str, exclude_id: Optional[int] = None):
    """
    Verifica si una matrícula ya está registrada
    
    Args:
        db: Sesión de base de datos
        matricula: Matrícula a verificar
        exclude_id: ID del kinesiólogo a excluir (para updates)
        
    Raises:
        HTTPException 400: Si la matrícula ya existe
    """
    query = db.query(Kinesiologo).filter(Kinesiologo.matricula_profesional == matricula)
    if exclude_id:
        query = query.filter(Kinesiologo.id != exclude_id)
    
    if query.first():
        raise HTTPException(
            status_code=400, 
            detail=MensajesError.matricula_duplicada(matricula)
        )

def verificar_usuario_existe(db: Session, user_id: int) -> User:
    """
    Verifica que un usuario exista
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        
    Returns:
        Usuario encontrado
        
    Raises:
        HTTPException 404: Si el usuario no existe
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404, 
            detail=MensajesError.USUARIO_NO_ENCONTRADO
        )
    return user

def verificar_perfil_no_existe(db: Session, user_id: int):
    """
    Verifica que un usuario no tenga perfil de kinesiólogo
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        
    Raises:
        HTTPException 400: Si el usuario ya tiene perfil
    """
    if db.query(Kinesiologo).filter(Kinesiologo.user_id == user_id).first():
        raise HTTPException(
            status_code=400, 
            detail=MensajesError.PERFIL_YA_EXISTE
        )

def verificar_sin_turnos_activos(db: Session, kinesiologo_id: int):
    """
    Verifica que un kinesiólogo no tenga turnos activos antes de eliminarlo
    
    Args:
        db: Sesión de base de datos
        kinesiologo_id: ID del kinesiólogo
        
    Raises:
        HTTPException 400: Si tiene turnos activos
    """
    turnos_pendientes = db.query(Turno).filter(
        Turno.kinesiologo_id == kinesiologo_id,
        Turno.estado.in_(["pendiente", "confirmado"])
    ).count()
    
    if turnos_pendientes > 0:
        raise HTTPException(
            status_code=400, 
            detail=MensajesError.kinesiologo_con_n_turnos(turnos_pendientes)
        )

# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/usuarios-disponibles", response_model=list[dict])
def obtener_usuarios_disponibles(db: Session = Depends(get_db)):
    """
    Obtiene lista de usuarios con rol kinesiólogo que no tienen perfil creado
    
    Returns:
        Lista de usuarios disponibles para crear perfil
    """
    usuarios_con_rol = (
        db.query(User).join(User.roles)
        .filter(Role.name == "kinesiologo")
        .options(joinedload(User.roles)).all()
    )
    
    usuarios_disponibles = []
    for user in usuarios_con_rol:
        tiene_perfil = db.query(Kinesiologo).filter(Kinesiologo.user_id == user.id).first()
        if not tiene_perfil:
            usuarios_disponibles.append({
                "id": user.id, 
                "nombre": user.nombre, 
                "email": user.email
            })
    
    return usuarios_disponibles

@router.get("/", response_model=list[KinesiologoOut])
def listar_kinesiologos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lista todos los kinesiólogos con paginación
    
    Args:
        skip: Número de registros a saltar
        limit: Número máximo de registros a retornar
        
    Returns:
        Lista de kinesiólogos
    """
    return kinesiologo_crud.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=KinesiologoOut, status_code=201)
def crear_kinesiologo(kinesiologo: KinesiologoCreate, db: Session = Depends(get_db)):
    """
    Crea un perfil de kinesiólogo para un usuario existente
    
    Args:
        kinesiologo: Datos del perfil de kinesiólogo
        
    Returns:
        Kinesiólogo creado
        
    Raises:
        HTTPException 404: Si el usuario no existe
        HTTPException 400: Si el usuario ya tiene perfil o la matrícula está duplicada
    """
    # Validar que el usuario exista
    verificar_usuario_existe(db, kinesiologo.user_id)
    
    # Validar que no tenga perfil ya
    verificar_perfil_no_existe(db, kinesiologo.user_id)
    
    # Validar matrícula duplicada
    verificar_matricula_existente(db, kinesiologo.matricula_profesional)
    
    # Capitalizar especialidad si existe
    if kinesiologo.especialidad:
        kinesiologo.especialidad = kinesiologo.especialidad.title()
    
    return kinesiologo_crud.create(db, kinesiologo)

@router.post("/con-usuario", response_model=KinesiologoOut, status_code=201)
def crear_kinesiologo_con_usuario(kinesiologo_data: dict, db: Session = Depends(get_db)):
    """
    Crea un kinesiólogo completo (usuario + perfil) en una sola operación
    
    Args:
        kinesiologo_data: Dict con datos del usuario y perfil
            - nombre: str (requerido)
            - email: str (requerido)
            - password: str (requerido)
            - matricula_profesional: str (requerido)
            - especialidad: str (opcional)
            
    Returns:
        Kinesiólogo creado con usuario asociado
        
    Raises:
        HTTPException 400: Si hay errores de validación o datos duplicados
        HTTPException 500: Si no se encuentra el rol kinesiólogo
    """
    # Validar y limpiar email
    if "email" not in kinesiologo_data or not kinesiologo_data["email"]:
        raise HTTPException(status_code=400, detail="El email es obligatorio")
    
    email_limpio = validar_email_formato(kinesiologo_data["email"])
    
    # Validar y limpiar nombre
    if "nombre" not in kinesiologo_data or not kinesiologo_data["nombre"].strip():
        raise HTTPException(status_code=400, detail="El nombre es obligatorio")
    
    nombre_limpio = capitalizar_texto(kinesiologo_data["nombre"])
    
    # Validar password
    if "password" not in kinesiologo_data or not kinesiologo_data["password"].strip():
        raise HTTPException(status_code=400, detail="La contraseña es obligatoria")
    
    # Validar matrícula
    if "matricula_profesional" not in kinesiologo_data or not kinesiologo_data["matricula_profesional"].strip():
        raise HTTPException(status_code=400, detail="La matrícula profesional es obligatoria")
    
    matricula_limpia = kinesiologo_data["matricula_profesional"].strip()
    
    # Validar unicidad de email
    if db.query(User).filter(User.email == email_limpio).first():
        raise HTTPException(
            status_code=400, 
            detail=MensajesError.email_duplicado(email_limpio)
        )
    
    # Validar unicidad de matrícula
    verificar_matricula_existente(db, matricula_limpia)
    
    # Crear Usuario
    nuevo_usuario = User(
        nombre=nombre_limpio,
        email=email_limpio,
        password_hash=get_password_hash(kinesiologo_data["password"]),
        activo=True
    )
    db.add(nuevo_usuario)
    db.flush()
    
    # Asignar rol kinesiólogo
    rol_kine = db.query(Role).filter(Role.name == "kinesiologo").first()
    if not rol_kine:
        raise HTTPException(
            status_code=500, 
            detail="Error de configuración: rol 'kinesiologo' no encontrado en el sistema"
        )
    
    user_role = UserRole(user_id=nuevo_usuario.id, role_id=rol_kine.id)
    db.add(user_role)
    
    # Crear Perfil Kinesiólogo
    nuevo_kinesiologo = Kinesiologo(
        user_id=nuevo_usuario.id,
        matricula_profesional=matricula_limpia,
        especialidad=capitalizar_texto(kinesiologo_data.get("especialidad", ""))
    )
    db.add(nuevo_kinesiologo)
    
    try:
        db.commit()
        db.refresh(nuevo_kinesiologo)
        return nuevo_kinesiologo
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error al crear el kinesiólogo: {str(e)}"
        )

@router.get("/{kinesiologo_id}", response_model=KinesiologoOut)
def obtener_kinesiologo(kinesiologo_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un kinesiólogo por ID
    
    Args:
        kinesiologo_id: ID del kinesiólogo
        
    Returns:
        Datos del kinesiólogo
        
    Raises:
        HTTPException 404: Si el kinesiólogo no existe
    """
    return kinesiologo_crud.get_or_404(db, kinesiologo_id)

@router.put("/{kinesiologo_id}", response_model=KinesiologoOut)
def actualizar_kinesiologo(
    kinesiologo_id: int, 
    kinesiologo: KinesiologoUpdate, 
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos de un kinesiólogo
    
    Args:
        kinesiologo_id: ID del kinesiólogo
        kinesiologo: Datos a actualizar
        
    Returns:
        Kinesiólogo actualizado
        
    Raises:
        HTTPException 404: Si el kinesiólogo no existe
        HTTPException 400: Si la nueva matrícula ya está en uso
    """
    db_kine = kinesiologo_crud.get(db, kinesiologo_id)
    if not db_kine:
        raise HTTPException(
            status_code=404, 
            detail=MensajesError.KINESIOLOGO_NO_ENCONTRADO
        )
    
    # Si intentan cambiar la matrícula, verificar que no esté duplicada
    if kinesiologo.matricula_profesional and kinesiologo.matricula_profesional != db_kine.matricula_profesional:
        verificar_matricula_existente(db, kinesiologo.matricula_profesional, exclude_id=kinesiologo_id)
    
    # Capitalizar especialidad si se proporciona
    if kinesiologo.especialidad:
        kinesiologo.especialidad = kinesiologo.especialidad.title()
    
    return kinesiologo_crud.update(db, kinesiologo_id, kinesiologo)

@router.delete("/{kinesiologo_id}")
def eliminar_kinesiologo(kinesiologo_id: int, db: Session = Depends(get_db)):
    """
    Elimina un kinesiólogo si no tiene turnos activos
    
    Args:
        kinesiologo_id: ID del kinesiólogo
        
    Returns:
        Mensaje de confirmación
        
    Raises:
        HTTPException 404: Si el kinesiólogo no existe
        HTTPException 400: Si tiene turnos activos (pendientes o confirmados)
    """
    kine = db.query(Kinesiologo).filter(Kinesiologo.id == kinesiologo_id).first()
    if not kine:
        raise HTTPException(
            status_code=404, 
            detail=MensajesError.KINESIOLOGO_NO_ENCONTRADO
        )
    
    # Verificar que no tenga turnos activos
    verificar_sin_turnos_activos(db, kinesiologo_id)
    
    try:
        db.delete(kine)
        db.commit()
        return {"message": "Kinesiólogo eliminado correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error al eliminar el kinesiólogo: {str(e)}"
        )
