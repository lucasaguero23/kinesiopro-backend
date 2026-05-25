from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


# ==========================================
# BASE
# ==========================================
class HistoriaClinicaBase(BaseModel):
    paciente_id: int
    kinesiologo_id: int
    fecha_consulta: Optional[datetime] = None
    motivo_consulta: str

    diagnostico: Optional[str] = None
    tratamiento: Optional[str] = None
    observaciones: Optional[str] = None
    peso: Optional[float] = None
    presion_arterial: Optional[str] = None


# ==========================================
# CREATE
# ==========================================
class HistoriaClinicaCreate(HistoriaClinicaBase):
    pass


# ==========================================
# UPDATE
# ==========================================
class HistoriaClinicaUpdate(BaseModel):
    fecha_consulta: Optional[datetime] = None
    motivo_consulta: Optional[str] = None
    diagnostico: Optional[str] = None
    tratamiento: Optional[str] = None
    observaciones: Optional[str] = None
    peso: Optional[float] = None
    presion_arterial: Optional[str] = None

    

# ==========================================
# OUT
# ==========================================
class HistoriaClinicaOut(HistoriaClinicaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
