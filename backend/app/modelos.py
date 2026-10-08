"""Registro de tablas: importa los modelos de cada módulo para que SQLAlchemy y Alembic vean el esquema completo.

Al crear un módulo con tablas, se agrega aquí su `models`.
"""
from app.core.db import Base
from app.acceso import models as acceso  # noqa: F401
from app.auditoria import models as auditoria  # noqa: F401
from app.operacion import models as operacion  # noqa: F401
from app.satelital import models as satelital  # noqa: F401

metadata = Base.metadata
