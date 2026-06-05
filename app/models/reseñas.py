from models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Uuid, DateTime, Integer
from datetime import datetime
from uuid import uuid4, UUID

class Reseña(Base):
    __tablename__ = "RESEÑAS"

    uuid: Mapped[UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=uuid4)
    uuid_usuario: Mapped[UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("USUARIOS.uuid"), nullable=False)
    uuid_empresa: Mapped[UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("EMPRESAS.uuid"), nullable=False)
    calificacion: Mapped[int] = mapped_column(Integer, nullable=False)
    comentario: Mapped[str] = mapped_column(String(255), nullable=True)
    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    
    
