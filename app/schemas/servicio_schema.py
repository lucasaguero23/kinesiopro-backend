from pydantic import BaseModel
from typing import Optional

class ServicioBase(BaseModel):
    nombre: str
    description: Optional[str] = None
    duracion_minutos: int

class ServicioCreate(ServicioBase):
    pass

class ServicioUpdate(BaseModel):
    """Schema para actualizar servicio (todos los campos opcionales)"""
    nombre: Optional[str] = None
    description: Optional[str] = None
    duracion_minutos: Optional[int] = None

    class Config:
        from_attributes = True  # <--- Cambiado

class ServicioOut(ServicioBase):
    id: int

    class Config:
        from_attributes = True  # <--- Cambiado