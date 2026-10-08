"""Estado técnico de entrega; no contiene reglas ni credenciales de negocio."""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import DateTime, ForeignKey, Index, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base, now


class EntregaPendiente(Base):
    __tablename__ = "entregas_pendientes"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    transportadora_id: Mapped[int] = mapped_column(ForeignKey("transportadoras.id"))
    evento: Mapped[str] = mapped_column(String(100))
    destinatario: Mapped[str] = mapped_column(String(100))
    clave: Mapped[str] = mapped_column(String(200))
    datos: Mapped[dict] = mapped_column(JSON)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")
    intentos: Mapped[int] = mapped_column(default=0)
    proximo_intento: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    reclamacion: Mapped[str | None] = mapped_column(String(36))
    reclamada_hasta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_codigo: Mapped[str | None] = mapped_column(String(100))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    terminado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (UniqueConstraint("transportadora_id", "destinatario", "clave"),
                     Index("ix_entregas_estado_proximo", "estado", "proximo_intento"))
