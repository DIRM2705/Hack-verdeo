from models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Uuid
from uuid import uuid4, UUID

class Empresa(Base):
    __tablename__ = "EMPRESAS"
    
    uuid: Mapped[UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=uuid4)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    calle: Mapped[str] = mapped_column(String(255), nullable=False)
    numero: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_interior: Mapped[int] = mapped_column(Integer, nullable=True)
    colonia: Mapped[str] = mapped_column(String(255), nullable=False)
    ciudad: Mapped[str] = mapped_column(String(255), nullable=False)
    estado: Mapped[str] = mapped_column(String(255), nullable=False)
    
    
