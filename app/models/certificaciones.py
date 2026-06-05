from models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Uuid, DateTime
from uuid import uuid4, UUID
from datetime import datetime

class Certificacion(Base):
    __tablename__ = "CERTIFICACIONES"
    
    uuid: Mapped[UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=uuid4)
    empresa_uuid: Mapped[UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("EMPRESAS.uuid"), nullable=False)
    fecha_vencimiento: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    url_certificado: Mapped[str] = mapped_column(String(255), nullable=False)
    
