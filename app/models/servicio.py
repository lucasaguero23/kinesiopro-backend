from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Servicio(Base):
    __tablename__ = "servicios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    duracion_minutos = Column(Integer, nullable=False)

    turnos = relationship("Turno", back_populates="servicio")
