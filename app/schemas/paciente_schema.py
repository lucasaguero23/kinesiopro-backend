from pydantic import BaseModel, field_validator
from typing import Optional
from app.schemas.user_schema import UserOut
from app.core.validaciones import validar_dni, validar_telefono, capitalizar_texto

class PacienteBase(BaseModel):
    dni: Optional[str] = None
    telefono: Optional[str] = None
    obra_social: Optional[str] = None
    historial_medico: Optional[str] = None
    direccion: Optional[str] = None

    @field_validator('dni')
    def validar_dni_field(cls, v):
        """Valida formato de DNI usando función centralizada"""
        return validar_dni(v)

    @field_validator('telefono')
    def validar_telefono_field(cls, v):
        """Valida formato de teléfono usando función centralizada"""
        return validar_telefono(v)

    @field_validator('obra_social', 'direccion')
    def capitalizar_textos(cls, v):
        """Capitaliza textos automáticamente"""
        return capitalizar_texto(v)
    
    @field_validator('historial_medico')
    def limpiar_historial(cls, v):
        """Limpia espacios innecesarios del historial médico"""
        if not v or v.strip() == '':
            return None
        return v.strip()

class PacienteCreate(PacienteBase):
    user_id: int

class PacienteUpdate(BaseModel):
    """Schema para actualizar paciente (todos los campos opcionales)"""
    dni: Optional[str] = None
    telefono: Optional[str] = None
    obra_social: Optional[str] = None
    historial_medico: Optional[str] = None
    direccion: Optional[str] = None

    @field_validator('dni')
    def validar_dni_field(cls, v):
        """Valida formato de DNI usando función centralizada"""
        return validar_dni(v)

    @field_validator('telefono')
    def validar_telefono_field(cls, v):
        """Valida formato de teléfono usando función centralizada"""
        return validar_telefono(v)
    
    @field_validator('obra_social', 'direccion')
    def capitalizar_textos(cls, v):
        """Capitaliza textos automáticamente"""
        return capitalizar_texto(v)
    
    @field_validator('historial_medico')
    def limpiar_historial(cls, v):
        """Limpia espacios innecesarios del historial médico"""
        if not v or v.strip() == '':
            return None
        return v.strip()

    class Config:
        from_attributes = True

class PacienteOut(PacienteBase):
    id: int
    user_id: int
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True
