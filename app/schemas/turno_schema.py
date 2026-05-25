from pydantic import BaseModel
from typing import Optional
from datetime import date, time
from app.schemas.paciente_schema import PacienteOut
from app.schemas.kinesiologo_schema import KinesiologoOut
from app.schemas.servicio_schema import ServicioOut
from app.schemas.sala_schema import SalaOut

class TurnoBase(BaseModel):
    fecha: date
    hora_inicio: time
    hora_fin: Optional[time] = None 
    estado: str
    motivo: Optional[str] = None
    observaciones: Optional[str] = None
    paciente_id: int
    kinesiologo_id: Optional[int] = None
    servicio_id: Optional[int] = None
    sala_id: Optional[int] = None

class TurnoCreate(TurnoBase):
    pass

class TurnoUpdate(BaseModel):
    fecha: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    estado: Optional[str] = None
    motivo: Optional[str] = None
    observaciones: Optional[str] = None
    paciente_id: Optional[int] = None
    kinesiologo_id: Optional[int] = None
    servicio_id: Optional[int] = None
    sala_id: Optional[int] = None

    class Config:
        from_attributes = True

class TurnoOut(TurnoBase):
    id: int
    paciente: Optional[PacienteOut]
    kinesiologo: Optional[KinesiologoOut]
    servicio: Optional[ServicioOut]
    sala: Optional[SalaOut]

    class Config:
        from_attributes = True