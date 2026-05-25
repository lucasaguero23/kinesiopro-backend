from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.core.crud import paciente_crud
from app.schemas.paciente_schema import PacienteCreate, PacienteUpdate, PacienteOut
from app.core.validaciones import validar_email_formato, MensajesError, capitalizar_texto
from app.models.user import User
from app.models.paciente import Paciente
from app.models.role import Role

router = APIRouter(
    prefix="/pacientes",
    tags=["Pacientes"]
)

# ═══════════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES DE VALIDACIÓN
# ═══════════════════════════════════════════════════════════════════════════

def verificar_dni_existente(db: Session, dni: str, exclude_id: int = None):
    """
    Verifica si un DNI ya está registrado
    
    Args:
        db: Sesión de base de datos
        dni: DNI a verificar
        exclude_id: ID del paciente a excluir (para updates)
        
    Raises:
        HTTPException 400: Si el DNI ya existe
    """
    if not dni:
        return
    
    query = db.query(Paciente).filter(Paciente.dni == dni)
    if exclude_id:
        query = query.filter(Paciente.id != exclude_id)
    
    if query.first():
        raise HTTPException(
            status_code=400, 
            detail=MensajesError.dni_duplicado(dni)
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
    Verifica que un usuario no tenga perfil de paciente
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        
    Raises:
        HTTPException 400: Si el usuario ya tiene perfil
    """
    if db.query(Paciente).filter(Paciente.user_id == user_id).first():
        raise HTTPException(
            status_code=400, 
            detail=MensajesError.PERFIL_YA_EXISTE
        )

# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/usuarios-disponibles", response_model=list[dict])
def obtener_usuarios_disponibles(db: Session = Depends(get_db)):
    """
    Obtiene lista de usuarios con rol paciente que no tienen perfil creado
    
    Returns:
        Lista de usuarios disponibles para crear perfil
    """
    usuarios_con_rol = (
        db.query(User).join(User.roles)
        .filter(Role.name == "paciente")
        .options(joinedload(User.roles)).all()
    )
    
    usuarios_disponibles = []
    for user in usuarios_con_rol:
        tiene_perfil = db.query(Paciente).filter(Paciente.user_id == user.id).first()
        if not tiene_perfil:
            usuarios_disponibles.append({
                "id": user.id, 
                "nombre": user.nombre, 
                "email": user.email
            })
    
    return usuarios_disponibles

@router.get("/", response_model=list[PacienteOut])
def listar_pacientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lista todos los pacientes con paginación
    
    Args:
        skip: Número de registros a saltar
        limit: Número máximo de registros a retornar
        
    Returns:
        Lista de pacientes
    """
    return paciente_crud.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=PacienteOut, status_code=201)
def crear_paciente(paciente: PacienteCreate, db: Session = Depends(get_db)):
    """
    Crea un perfil de paciente para un usuario existente
    
    Args:
        paciente: Datos del perfil de paciente
        
    Returns:
        Paciente creado
        
    Raises:
        HTTPException 404: Si el usuario no existe
        HTTPException 400: Si el usuario ya tiene perfil o el DNI está duplicado
    """
    # Validar que el usuario exista
    verificar_usuario_existe(db, paciente.user_id)
    
    # Validar que no tenga perfil ya
    verificar_perfil_no_existe(db, paciente.user_id)
    
    # Validar DNI duplicado
    if paciente.dni:
        verificar_dni_existente(db, paciente.dni)
    
    return paciente_crud.create(db, paciente)

@router.post("/con-usuario", response_model=PacienteOut, status_code=201)
def crear_paciente_con_usuario(paciente_data: dict, db: Session = Depends(get_db)):
    """
    Crea un paciente completo (usuario + perfil) en una sola operación
    
    Args:
        paciente_data: Dict con datos del usuario y perfil
            - nombre: str (requerido)
            - email: str (requerido)
            - password: str (requerido)
            - dni: str (opcional)
            - telefono: str (opcional)
            - obra_social: str (opcional)
            - historial_medico: str (opcional)
            - direccion: str (opcional)
            
    Returns:
        Paciente creado con usuario asociado
        
    Raises:
        HTTPException 400: Si hay errores de validación o datos duplicados
        HTTPException 500: Si no se encuentra el rol paciente
    """
    from app.core.security import get_password_hash
    from app.models.user_role import UserRole
    
    # Validar y limpiar email
    if "email" not in paciente_data or not paciente_data["email"]:
        raise HTTPException(status_code=400, detail="El email es obligatorio")
    
    email_limpio = validar_email_formato(paciente_data["email"])
    
    # Validar y limpiar nombre
    if "nombre" not in paciente_data or not paciente_data["nombre"].strip():
        raise HTTPException(status_code=400, detail="El nombre es obligatorio")
    
    nombre_limpio = capitalizar_texto(paciente_data["nombre"])
    
    # Validar password
    if "password" not in paciente_data or not paciente_data["password"].strip():
        raise HTTPException(status_code=400, detail="La contraseña es obligatoria")
    
    # Limpiar DNI si existe
    dni_limpio = None
    if paciente_data.get("dni"):
        dni_limpio = paciente_data["dni"].replace(".", "").replace(" ", "").strip()
    
    # Validar unicidad de email
    if db.query(User).filter(User.email == email_limpio).first():
        raise HTTPException(
            status_code=400, 
            detail=MensajesError.email_duplicado(email_limpio)
        )
    
    # Validar unicidad de DNI
    if dni_limpio:
        verificar_dni_existente(db, dni_limpio)
    
    # Crear Usuario
    nuevo_usuario = User(
        nombre=nombre_limpio,
        email=email_limpio,
        password_hash=get_password_hash(paciente_data["password"]),
        activo=True
    )
    db.add(nuevo_usuario)
    db.flush()
    
    # Asignar rol paciente
    rol_paciente = db.query(Role).filter(Role.name == "paciente").first()
    if not rol_paciente:
        raise HTTPException(
            status_code=500, 
            detail="Error de configuración: rol 'paciente' no encontrado en el sistema"
        )
    
    user_role = UserRole(user_id=nuevo_usuario.id, role_id=rol_paciente.id)
    db.add(user_role)
    
    # Crear Perfil Paciente
    nuevo_paciente = Paciente(
        user_id=nuevo_usuario.id,
        dni=dni_limpio,
        telefono=paciente_data.get("telefono"),
        obra_social=capitalizar_texto(paciente_data.get("obra_social", "")),
        historial_medico=paciente_data.get("historial_medico"),
        direccion=capitalizar_texto(paciente_data.get("direccion", ""))
    )
    db.add(nuevo_paciente)
    
    try:
        db.commit()
        db.refresh(nuevo_paciente)
        return nuevo_paciente
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error al crear el paciente: {str(e)}"
        )

@router.get("/{paciente_id}", response_model=PacienteOut)
def obtener_paciente(paciente_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un paciente por ID
    
    Args:
        paciente_id: ID del paciente
        
    Returns:
        Datos del paciente
        
    Raises:
        HTTPException 404: Si el paciente no existe
    """
    return paciente_crud.get_or_404(db, paciente_id)

@router.put("/{paciente_id}", response_model=PacienteOut)
def actualizar_paciente(
    paciente_id: int, 
    paciente: PacienteUpdate, 
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos de un paciente
    
    Args:
        paciente_id: ID del paciente
        paciente: Datos a actualizar
        
    Returns:
        Paciente actualizado
        
    Raises:
        HTTPException 404: Si el paciente no existe
        HTTPException 400: Si el nuevo DNI ya está en uso
    """
    db_paciente = paciente_crud.get(db, paciente_id)
    if not db_paciente:
        raise HTTPException(
            status_code=404, 
            detail=MensajesError.PACIENTE_NO_ENCONTRADO
        )
    
    # Si intentan cambiar el DNI, verificar que no esté duplicado
    if paciente.dni and paciente.dni != db_paciente.dni:
        verificar_dni_existente(db, paciente.dni, exclude_id=paciente_id)
    
    return paciente_crud.update(db, paciente_id, paciente)

@router.delete("/{paciente_id}")
def eliminar_paciente(paciente_id: int, db: Session = Depends(get_db)):
    """
    Elimina un paciente
    
    Args:
        paciente_id: ID del paciente
        
    Returns:
        Mensaje de confirmación
        
    Raises:
        HTTPException 404: Si el paciente no existe
    """
    deleted = paciente_crud.delete(db, paciente_id)
    if not deleted:
        raise HTTPException(
            status_code=404, 
            detail=MensajesError.PACIENTE_NO_ENCONTRADO
        )
    return {"message": "Paciente eliminado correctamente"}
