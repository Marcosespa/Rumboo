from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base, now


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
