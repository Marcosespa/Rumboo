from datetime import datetime
from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base, now

ACTIVE_STATES = ("registrado", "programado", "en_ruta", "con_novedad")


class Transportadora(Base):
    __tablename__ = "transportadoras"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200))
    nit: Mapped[str] = mapped_column(String(30), default="")
    frecuencia_consulta_min: Mapped[int] = mapped_column(default=5)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    __table_args__ = (CheckConstraint("frecuencia_consulta_min BETWEEN 5 AND 10"),)


class Usuario(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    transportadora_id: Mapped[int] = mapped_column(ForeignKey("transportadoras.id"), index=True)
    usuario: Mapped[str] = mapped_column(String(100), unique=True)
    nombre: Mapped[str] = mapped_column(String(200))
    password_hash: Mapped[str] = mapped_column(String(200))
    activo: Mapped[bool] = mapped_column(default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    transportadora: Mapped[Transportadora] = relationship()


class Sesion(Base):
    __tablename__ = "sesiones"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    expira_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    usuario: Mapped[Usuario] = relationship()


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


class Evento(Base):
    __tablename__ = "eventos"
    id: Mapped[int] = mapped_column(primary_key=True)
    transportadora_id: Mapped[int] = mapped_column(ForeignKey("transportadoras.id"), index=True)
    viaje_id: Mapped[int | None] = mapped_column(ForeignKey("viajes.id"), index=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    tipo: Mapped[str] = mapped_column(String(80))
    detalle: Mapped[dict] = mapped_column(JSON, default=dict)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
