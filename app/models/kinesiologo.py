from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Kinesiologo(Base):
    __tablename__ = "kinesiologos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    matricula_profesional = Column(String(50), unique=True, nullable=False)
    especialidad = Column(String(100))

    # Relación con usuario
    user = relationship("User", back_populates="kinesiologo")

    # Relación con turnos
    turnos = relationship("Turno", back_populates="kinesiologo", cascade="all, delete-orphan")

    # Relación con horarios
    horarios = relationship("HorarioKinesiologo", back_populates="kinesiologo", cascade="all, delete-orphan")
    
    # ✨ NUEVA: Relación con historias clínicas
    historias_clinicas = relationship(
        "HistoriaClinica",
        back_populates="kinesiologo"
    )