from models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Uuid, Float
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
    latitud: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    longitud: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    def to_dict(self):
        return {
            "uuid": str(self.uuid),
            "nombre": self.nombre,
            "calle": self.calle,
            "numero": self.numero,
            "numero_interior": self.numero_interior,
            "colonia": self.colonia,
            "ciudad": self.ciudad,
            "estado": self.estado,
            "latitud": self.latitud,
            "longitud": self.longitud
        }
    
    
