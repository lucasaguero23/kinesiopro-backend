from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.core.token import create_access_token
from app.core.security import verify_password, get_password_hash

from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.schemas.user_schema import UserCreate
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["Autenticación"])

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# 🔐 LOGIN
@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")

    if not user.activo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo")

    access_token_expires = timedelta(minutes=60 * 24) # 24 horas
    
    # 🔴 CORRECCIÓN: 
    # 1. 'sub' debe ser el EMAIL (porque security.py busca por email).
    # 2. Agregamos 'id' explícitamente para que el Front lo lea fácil.
    access_token = create_access_token(
        data={"sub": user.email, "id": user.id}, 
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

# 🧾 REGISTRO
@router.post("/register")
def register(new_user: UserCreate, db: Session = Depends(get_db)):
    user_exist = db.query(User).filter(User.email == new_user.email).first()
    if user_exist:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    hashed_pw = get_password_hash(new_user.password)
    user = User(nombre=new_user.nombre, email=new_user.email, password_hash=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)

    # Asigna rol de paciente por defecto
    role = db.query(Role).filter(Role.name == "paciente").first()
    if role:
        user_role = UserRole(user_id=user.id, role_id=role.id)
        db.add(user_role)
        db.commit()

    return {"message": "Usuario registrado correctamente"}