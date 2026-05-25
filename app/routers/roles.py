from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.role import Role
from app.schemas.role_schema import RoleCreate, RoleResponse
from app.models.user import User

from app.core.permissions import role_required
# 🔴 CAMBIO AQUÍ: Importar desde security, NO desde token
from app.core.security import get_current_user 

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)

# 🧩 Crear rol (solo admin)
@router.post("/", response_model=RoleResponse, dependencies=[Depends(role_required("admin"))])
def crear_rol(rol: RoleCreate, db: Session = Depends(get_db)):
    existente = db.query(Role).filter(Role.name == rol.name).first()
    if existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El rol ya existe")

    nuevo_rol = Role(name=rol.name, description=rol.description)
    db.add(nuevo_rol)
    db.commit()
    db.refresh(nuevo_rol)
    return nuevo_rol

# 📋 Listar roles (solo admin)
@router.get("/", response_model=list[RoleResponse], dependencies=[Depends(role_required("admin"))])
def listar_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()

# 🗑️ Eliminar rol (solo admin)
@router.delete("/{rol_id}", dependencies=[Depends(role_required("admin"))])
def eliminar_rol(rol_id: int, db: Session = Depends(get_db)):
    rol = db.query(Role).filter(Role.id == rol_id).first()
    if not rol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
    db.delete(rol)
    db.commit()
    return {"mensaje": "Rol eliminado correctamente"}

# ➕ Asignar rol a usuario
@router.post("/{user_id}/roles/{role_id}", dependencies=[Depends(role_required("admin"))])
def asignar_rol_a_usuario(user_id: int, role_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    rol = db.query(Role).filter(Role.id == role_id).first()
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    if any(r.id == role_id for r in user.roles):
        raise HTTPException(status_code=400, detail="El usuario ya tiene ese rol asignado")

    user.roles.append(rol)
    db.commit()
    return {"message": f"Rol '{rol.name}' asignado a {user.nombre} correctamente."}

# 🗑️ Remover rol de usuario
@router.delete("/{user_id}/roles/{role_id}", dependencies=[Depends(role_required("admin"))])
def remover_rol_de_usuario(user_id: int, role_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    rol = db.query(Role).filter(Role.id == role_id).first()
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    if not any(r.id == role_id for r in user.roles):
        raise HTTPException(status_code=400, detail="El usuario no tiene ese rol asignado")

    user.roles.remove(rol)
    db.commit()
    return {"message": f"Rol '{rol.name}' removido de {user.nombre} correctamente."}