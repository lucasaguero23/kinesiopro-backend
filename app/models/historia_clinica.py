from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class HistoriaClinica(Base):
    __tablename__ = "historias_clinicas"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=False)
    kinesiologo_id = Column(Integer, ForeignKey("kinesiologos.id"), nullable=False)
    turno_id = Column(Integer, ForeignKey("turnos.id"), nullable=True)  # Opcional: asociar a turno
    
    # Fecha de la consulta
    fecha_consulta = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Datos vitales
    peso = Column(Float, nullable=True)  # kg
    altura = Column(Float, nullable=True)  # cm
    presion_arterial = Column(String(20), nullable=True)  # ej: "120/80"
    frecuencia_cardiaca = Column(Integer, nullable=True)  # latidos por minuto
    temperatura = Column(Float, nullable=True)  # °C
    
    # Evaluación clínica
    motivo_consulta = Column(Text, nullable=False)
    diagnostico = Column(Text, nullable=True)
    tratamiento = Column(Text, nullable=True)
    evolucion = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)
    
    # Próxima consulta recomendada
    proxima_consulta = Column(DateTime, nullable=True)
    
    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    paciente = relationship("Paciente", back_populates="historias_clinicas")
    kinesiologo = relationship("Kinesiologo", back_populates="historias_clinicas")
    turno = relationship("Turno", back_populates="historia_clinica", uselist=False)
