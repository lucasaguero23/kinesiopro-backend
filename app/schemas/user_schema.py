from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from app.core.validaciones import validar_password_fuerte

# --- Schema para Roles ---
class RoleOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

# --- Schema Base para Usuarios ---
class UserBase(BaseModel):
    nombre: str
    email: EmailStr
    activo: Optional[bool] = True

class UserCreate(UserBase):
    password: str

    @field_validator('password')
    def password_must_be_strong(cls, v):
        """Valida que la contraseña sea segura"""
        return validar_password_fuerte(v)
    
    @field_validator('nombre')
    def nombre_no_vacio(cls, v):
        """Valida que el nombre no esté vacío"""
        if not v or v.strip() == '':
            raise ValueError('El nombre es obligatorio')
        if len(v.strip()) < 2:
            raise ValueError('El nombre debe tener al menos 2 caracteres')
        return v.strip()

class UserUpdate(BaseModel):
    """Schema para actualizar usuario (todos los campos opcionales)"""
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    activo: Optional[bool] = None
    password: Optional[str] = None 

    @field_validator('password')
    def password_must_be_strong(cls, v):
        """Valida contraseña solo si se proporciona"""
        if v and v.strip(): 
            return validar_password_fuerte(v)
        return v
    
    @field_validator('nombre')
    def nombre_no_vacio(cls, v):
        """Valida nombre solo si se proporciona"""
        if v is not None:
            if v.strip() == '':
                raise ValueError('El nombre no puede estar vacío')
            if len(v.strip()) < 2:
                raise ValueError('El nombre debe tener al menos 2 caracteres')
            return v.strip()
        return v

    class Config:
        from_attributes = True

class UserOut(UserBase):
    id: int
    roles: List[RoleOut] = []

    class Config:
        from_attributes = True
