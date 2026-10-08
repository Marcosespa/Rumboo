"""Pruebas sobre PostgreSQL real: las reservas, locks e índices parciales no se reproducen en SQLite.

Base de pruebas (desechable):
    docker run -d --name rumboo-test-db -e POSTGRES_USER=rumboo -e POSTGRES_PASSWORD=rumboo \
        -e POSTGRES_DB=rumboo_test -p 127.0.0.1:55432:5432 postgres:16-alpine
Otra base: TEST_DATABASE_URL=postgresql+psycopg://... uv run pytest
"""
import os
from pathlib import Path
import pytest
from alembic.config import Config
from alembic import command
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from app.acceso.servicio import create_user
from app.core.config import Settings
from app.core.db import make_engine
from app.main import create_app
from app.modelos import metadata
from app.satelital.cliente import ServicioSatelitalNoDisponible
from tests.ayudas import CALLBACK_SECRET, PASSWORD

BACKEND = Path(__file__).resolve().parents[1]
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "postgresql+psycopg://rumboo:rumboo@localhost:55432/rumboo_test")


def alembic_config():
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND / "alembic"))
    return config


class FakeSatrack:
    """Reemplaza a satelital.cliente.SatrackServiceClient: registra los jobs en vez de enviarlos."""

    def __init__(self):
        self.jobs = []
        self.available = True

    async def send_job(self, job):
        if not self.available:
            raise ServicioSatelitalNoDisponible()
        self.jobs.append(job)

    async def close(self):
        pass


@pytest.fixture(scope="session")
def engine():
    engine = make_engine(TEST_DATABASE_URL)
    try:
        with engine.begin() as connection:
            connection.execute(text("DROP SCHEMA public CASCADE"))
            connection.execute(text("CREATE SCHEMA public"))
    except OperationalError:
        pytest.exit(f"PostgreSQL de pruebas no disponible en {TEST_DATABASE_URL}; ver tests/conftest.py", returncode=2)
    command.upgrade(alembic_config(), "head")
    yield engine
    engine.dispose()


@pytest.fixture(autouse=True)
def clean(engine):
    yield
    with engine.begin() as connection:
        connection.execute(text(f"TRUNCATE {', '.join(t.name for t in metadata.sorted_tables)} RESTART IDENTITY CASCADE"))


@pytest.fixture
def settings():
    return Settings(_env_file=None, database_url=TEST_DATABASE_URL, secret_key="s" * 32, satrack_service_api_key="k" * 16,
                    callback_secret=CALLBACK_SECRET, scheduler_enabled=False)


@pytest.fixture
def satrack():
    return FakeSatrack()


@pytest.fixture
def app(engine, settings, satrack):
    return create_app(settings, engine, satrack)


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


@pytest.fixture
def login(app, client):
    def login(carrier="Transportes Uno", username="operador1"):
        with app.state.sessions() as db:
            create_user(db, carrier, username, PASSWORD)
        response = client.post("/api/auth/login", json={"usuario": username, "password": PASSWORD})
        assert response.status_code == 200
        return {"Authorization": f"Bearer {response.json()['token']}"}
    return login
