from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Index, JSON, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base, now


class CuentaSatelital(Base):
    __tablename__ = "cuentas_satelitales"
    id: Mapped[int] = mapped_column(primary_key=True)
    transportadora_id: Mapped[int] = mapped_column(ForeignKey("transportadoras.id"), unique=True)
    proveedor: Mapped[str] = mapped_column(String(30), default="satrack")
    usuario: Mapped[str] = mapped_column(String(200))
    password_cifrado: Mapped[str] = mapped_column(Text)
    version: Mapped[int] = mapped_column(default=1)
    estado: Mapped[str] = mapped_column(String(40), default="sin_verificar")
    fallos_consecutivos: Mapped[int] = mapped_column(default=0)
    ultima_consulta_ok: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ultimo_error: Mapped[str | None] = mapped_column(Text)
    backoff_hasta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ConsultaSatelital(Base):
    __tablename__ = "consultas_satelitales"
    job_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    transportadora_id: Mapped[int] = mapped_column(ForeignKey("transportadoras.id"), index=True)
    cuenta_satelital_id: Mapped[int] = mapped_column(ForeignKey("cuentas_satelitales.id"))
    cuenta_version: Mapped[int] = mapped_column(default=1)
    tipo: Mapped[str] = mapped_column(String(20))
    placas: Mapped[list] = mapped_column(JSON, default=list)
    enviado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    respondido_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")
    error_codigo: Mapped[str | None] = mapped_column(String(60))
    error_detalle: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (Index("uq_consulta_pendiente", "cuenta_satelital_id", unique=True,
        postgresql_where=text("estado = 'pendiente'"), sqlite_where=text("estado = 'pendiente'")),)


class Posicion(Base):
    __tablename__ = "posiciones"
    id: Mapped[int] = mapped_column(primary_key=True)
    transportadora_id: Mapped[int] = mapped_column(ForeignKey("transportadoras.id"), index=True)
    vehiculo_id: Mapped[int] = mapped_column(ForeignKey("vehiculos.id"))
    viaje_id: Mapped[int | None] = mapped_column(ForeignKey("viajes.id"))
    consulta_id: Mapped[str] = mapped_column(ForeignKey("consultas_satelitales.job_id"))
    lat: Mapped[float | None] = mapped_column(Float)
    lng: Mapped[float | None] = mapped_column(Float)
    velocidad_kmh: Mapped[float | None] = mapped_column(Float)
    direccion: Mapped[str] = mapped_column(Text, default="")
    estado_gps: Mapped[str] = mapped_column(String(80), default="")
    reportado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reportado_texto: Mapped[str] = mapped_column(String(250), default="")
    capturado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    __table_args__ = (UniqueConstraint("vehiculo_id", "reportado_en"), Index("ix_posiciones_viaje_fecha", "viaje_id", "capturado_en"))
