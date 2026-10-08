from datetime import datetime
from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base, now

ACTIVE_STATES = ("registrado", "programado", "en_ruta", "con_novedad")


class Conductor(Base):
    __tablename__ = "conductores"
    id: Mapped[int] = mapped_column(primary_key=True)
    transportadora_id: Mapped[int] = mapped_column(ForeignKey("transportadoras.id"), index=True)
    nombre: Mapped[str] = mapped_column(String(200))
    cedula: Mapped[str] = mapped_column(String(10))
    telefono: Mapped[str] = mapped_column(String(13))
    autoriza_contacto: Mapped[bool] = mapped_column(default=False)
    autorizado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (UniqueConstraint("transportadora_id", "cedula"),)


class Vehiculo(Base):
    __tablename__ = "vehiculos"
    id: Mapped[int] = mapped_column(primary_key=True)
    transportadora_id: Mapped[int] = mapped_column(ForeignKey("transportadoras.id"), index=True)
    placa: Mapped[str] = mapped_column(String(6))
    propietario: Mapped[str] = mapped_column(String(200), default="")
    en_satelital: Mapped[bool | None] = mapped_column(Boolean)
    ultima_posicion_id: Mapped[int | None] = mapped_column(Integer)
    __table_args__ = (UniqueConstraint("transportadora_id", "placa"),)


class Viaje(Base):
    __tablename__ = "viajes"
    id: Mapped[int] = mapped_column(primary_key=True)
    transportadora_id: Mapped[int] = mapped_column(ForeignKey("transportadoras.id"), index=True)
    manifiesto: Mapped[str] = mapped_column(String(40))
    conductor_id: Mapped[int] = mapped_column(ForeignKey("conductores.id"))
    vehiculo_id: Mapped[int] = mapped_column(ForeignKey("vehiculos.id"))
    origen: Mapped[str] = mapped_column(String(200))
    destino: Mapped[str] = mapped_column(String(200))
    salida_estimada: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    llegada_estimada: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    peso_salida_kg: Mapped[float] = mapped_column(Float)
    estado: Mapped[str] = mapped_column(String(30), default="registrado", index=True)
    motivo_cancelacion: Mapped[str | None] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    conductor: Mapped[Conductor] = relationship()
    vehiculo: Mapped[Vehiculo] = relationship()
    remesas: Mapped[list["Remesa"]] = relationship(cascade="all, delete-orphan")
    __table_args__ = (
        UniqueConstraint("transportadora_id", "manifiesto"),
        CheckConstraint("peso_salida_kg > 0"),
        CheckConstraint("llegada_estimada > salida_estimada"),
        Index("uq_viaje_vehiculo_activo", "vehiculo_id", unique=True,
              postgresql_where=text("estado IN ('registrado','programado','en_ruta','con_novedad')"),
              sqlite_where=text("estado IN ('registrado','programado','en_ruta','con_novedad')")),
        Index("uq_viaje_conductor_activo", "conductor_id", unique=True,
              postgresql_where=text("estado IN ('registrado','programado','en_ruta','con_novedad')"),
              sqlite_where=text("estado IN ('registrado','programado','en_ruta','con_novedad')")),
    )


class Remesa(Base):
    __tablename__ = "remesas"
    id: Mapped[int] = mapped_column(primary_key=True)
    transportadora_id: Mapped[int] = mapped_column(ForeignKey("transportadoras.id"), index=True)
    viaje_id: Mapped[int] = mapped_column(ForeignKey("viajes.id", ondelete="CASCADE"))
    numero: Mapped[str] = mapped_column(String(80))
    cliente: Mapped[str] = mapped_column(String(200))
    peso_kg: Mapped[float] = mapped_column(Float)
    cantidad: Mapped[int | None] = mapped_column(Integer)
    __table_args__ = (UniqueConstraint("viaje_id", "numero"), CheckConstraint("peso_kg > 0"))
