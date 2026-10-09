from alembic import command
from sqlalchemy import select, text
from app.satelital.models import VehiculoSatelital
from tests.conftest import alembic_config
from tests.ayudas import send_callback
from tests.satelital.test_flujo_satrack import connect_account


def test_migration_preserves_existing_vehicle_location(app, client, login, satrack, engine):
    headers = login()
    _, job = connect_account(client, headers, satrack)
    assert send_callback(client, job["job_id"], "vehicles", vehicles=[{
        "plate": "ABC123", "address": "Bogotá", "lat": 4.6, "lng": -74.1}]).status_code == 200
    with app.state.sessions() as db:
        state = db.scalar(select(VehiculoSatelital))
        vehicle_id, position_id = state.vehiculo_id, state.ultima_posicion_id
    config = alembic_config()
    command.downgrade(config, "5f22f636b715")
    try:
        with engine.connect() as db:
            previous = db.execute(text("SELECT en_satelital, ultima_posicion_id FROM vehiculos WHERE id=:id"), {"id": vehicle_id}).one()
            assert previous == (True, position_id)
    finally:
        command.upgrade(config, "head")
    with app.state.sessions() as db:
        migrated = db.get(VehiculoSatelital, vehicle_id)
        assert migrated.en_satelital and migrated.ultima_posicion_id == position_id
    assert client.get("/api/vehiculos", headers=headers).json()["items"][0]["ultima_posicion"]["direccion"] == "Bogotá"
    command.check(config)
