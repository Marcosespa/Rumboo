from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def now():
    return datetime.now(timezone.utc)


def aware(value):
    return value.replace(tzinfo=timezone.utc) if value and value.tzinfo is None else value


def make_engine(url):
    kwargs = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        from sqlalchemy.pool import StaticPool
        kwargs.update(connect_args={"check_same_thread": False}, poolclass=StaticPool)
    elif url.startswith("postgresql"):
        # Detecta una conexión caída (p. ej. la del advisory lock del runner) en vez de esperar indefinidamente.
        kwargs.update(connect_args={"keepalives": 1, "keepalives_idle": 30, "keepalives_interval": 10, "keepalives_count": 3})
    return create_engine(url, **kwargs)
