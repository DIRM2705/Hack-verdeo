from models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Uuid, DateTime
from datetime import datetime
from uuid import uuid4, UUID

class Usuario(Base):
    __tablename__ = "USUARIOS"

    uuid: Mapped[UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=uuid4)
    nombres: Mapped[str] = mapped_column(String(255), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(255), nullable=False)
    correo: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    contraseña: Mapped[str] = mapped_column(String(255), nullable=False)
    fecha_nacimiento: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    
