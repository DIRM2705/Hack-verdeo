from models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Uuid
from uuid import uuid4, UUID

class Badge(Base):
    __tablename__ = "BADGES"

    uuid: Mapped[UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=uuid4)
    empleados_uuid: Mapped[UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("EMPRESAS.uuid"), nullable=False)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    icono_url: Mapped[str] = mapped_column(String(255), nullable=False)
    
    
    
