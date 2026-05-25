from pydantic import BaseModel
from typing import Optional

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    """Schema para actualizar role (todos los campos opcionales)"""
    name: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True

class RoleResponse(RoleBase):
    id: int

    class Config:
        from_attributes = True

