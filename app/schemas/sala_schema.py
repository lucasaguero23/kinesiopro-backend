from pydantic import BaseModel
from typing import Optional

class SalaBase(BaseModel):
    nombre: str
    ubicacion: Optional[str] = None


class SalaCreate(SalaBase):
    pass


class SalaUpdate(BaseModel):
    """Schema para actualizar sala (todos los campos opcionales)"""
    nombre: Optional[str] = None
    ubicacion: Optional[str] = None

    class Config:
        from_attributes = True


class SalaOut(SalaBase):
    id: int

    class Config:
        from_attributes = True
