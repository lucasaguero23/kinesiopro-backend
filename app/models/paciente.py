from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    dni = Column(String(20), unique=True)
    telefono = Column(String(20))
    obra_social = Column(String(100))             
    historial_medico = Column(String(255))        
    direccion = Column(String(255))

    # 🔗 Relación con usuario
    user = relationship("User", back_populates="paciente")

    # 🔗 Relación con turnos (si la usás)
    turnos = relationship("Turno", back_populates="paciente", cascade="all, delete-orphan")

    historias_clinicas = relationship(
        "HistoriaClinica",
        back_populates="paciente",
        cascade="all, delete-orphan"
    )

