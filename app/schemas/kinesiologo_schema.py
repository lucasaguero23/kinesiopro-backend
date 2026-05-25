from pydantic import BaseModel, field_validator
from typing import Optional
from app.schemas.user_schema import UserOut
from app.core.validaciones import validar_matricula, capitalizar_texto


class KinesiologoBase(BaseModel):
    especialidad: Optional[str] = None
    matricula_profesional: Optional[str] = None
    
    @field_validator('especialidad')
    def capitalizar_especialidad(cls, v):
        """Capitaliza la especialidad automáticamente"""
        return capitalizar_texto(v)


class KinesiologoCreate(KinesiologoBase):
    user_id: int
    matricula_profesional: str  # Requerido en creación
    
    @field_validator('matricula_profesional')
    def validar_matricula_field(cls, v):
        """Valida que la matrícula no esté vacía y tenga formato válido"""
        if not v or v.strip() == '':
            raise ValueError('La matrícula profesional es obligatoria')
        
        matricula_validada = validar_matricula(v)
        if matricula_validada is None:
            raise ValueError('La matrícula profesional es obligatoria')
        
        return matricula_validada


class KinesiologoUpdate(BaseModel):
    """Schema para actualizar kinesiólogo (todos los campos opcionales)"""
    especialidad: Optional[str] = None
    matricula_profesional: Optional[str] = None
    
    @field_validator('especialidad')
    def capitalizar_especialidad(cls, v):
        """Capitaliza la especialidad automáticamente"""
        return capitalizar_texto(v)
    
    @field_validator('matricula_profesional')
    def validar_matricula_field(cls, v):
        """Valida matrícula solo si se proporciona"""
        if v is not None and v.strip() != '':
            return validar_matricula(v)
        return v

    class Config:
        from_attributes = True


class KinesiologoOut(KinesiologoBase):
    id: int
    user_id: int
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True
