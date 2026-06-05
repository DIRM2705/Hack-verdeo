from models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Uuid
from uuid import uuid4, UUID

class Empleado(Base):
    __tablename__ = "EMPLEADOS"

    uuid: Mapped[UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=uuid4)
    empresa_uuid: Mapped[UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("EMPRESAS.uuid"), nullable=False)
    nombres: Mapped[str] = mapped_column(String(255), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(255), nullable=False)
    
    
