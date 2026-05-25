from sqlalchemy import Column, Integer, Time, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class HorarioKinesiologo(Base):
    __tablename__ = "horarios_kinesiologo"

    id = Column(Integer, primary_key=True, index=True)
    kinesiologo_id = Column(Integer, ForeignKey("kinesiologos.id", ondelete="CASCADE"))
    dia_semana = Column(String(20), nullable=False)  # Lunes, Martes, etc.
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)

    # 🔗 Relación inversa con Kinesiologo
    kinesiologo = relationship("Kinesiologo", back_populates="horarios")
