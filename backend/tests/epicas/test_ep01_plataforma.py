"""EP-01 · Plataforma: salud del servicio y migraciones repetibles."""
from alembic import command
from tests.conftest import alembic_config


def test_health_reports_database_and_runner(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok" and body["database"] == "ok"
    assert {"scheduler", "tareas", "entregas"} <= body.keys()


def test_migrations_can_be_rebuilt_from_scratch(engine):
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    command.upgrade(config, "head")
    command.check(config)
