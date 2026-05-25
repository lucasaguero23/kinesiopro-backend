from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True)

    # 🔗 Roles (muchos a muchos)
    roles = relationship("Role", secondary="user_roles", back_populates="users")

    # 🔗 Relaciones 1 a 1 con perfiles
    paciente = relationship("Paciente", back_populates="user", uselist=False)
    kinesiologo = relationship("Kinesiologo", back_populates="user", uselist=False)
    