import asyncio
import time
from datetime import UTC, datetime, timedelta
from cryptography.fernet import Fernet
from sqlalchemy import select, update
from app.satelital import servicio
from app.satelital.models import ConsultaSatelital, CuentaSatelital
from tests.ayudas import send_callback, trip_body

ACCOUNT = {"usuario": "satrack-demo", "password": "clave-satrack"}


def connect_account(client, headers, satrack):
    response = client.put("/api/cuenta-satelital", json=ACCOUNT, headers=headers)
    assert response.status_code == 200
    return response.json(), satrack.jobs[-1]


def test_connecting_the_account_sends_a_fleet_job(client, login, satrack):
    headers = login()
    account, job = connect_account(client, headers, satrack)
    assert job["type"] == "vehicles"
    assert job["account"]["password"] == "clave-satrack"
    assert account["estado"] == "sin_verificar" and account["consulta_pendiente"]
    assert "clave-satrack" not in str(account)


def test_fleet_callback_schedules_registered_trips(client, login, satrack):
    headers = login()
    _, job = connect_account(client, headers, satrack)
    trip = client.post("/api/viajes", json=trip_body(), headers=headers).json()
    assert trip["estado"] == "registrado"
    assert len(satrack.jobs) == 1  # ya había una consulta pendiente: no se duplica
    assert send_callback(client, job["job_id"], "vehicles", vehicles=[{"plate": "ABC123"}]).json() == {"status": "ok"}
    trip = client.get(f"/api/viajes/{trip['id']}", headers=headers).json()
    assert trip["estado"] == "programado"
    assert trip["vehiculo"]["en_satelital"] is True
    assert client.get("/api/cuenta-satelital", headers=headers).json()["estado"] == "ok"


def test_new_trip_with_verified_plate_is_scheduled_immediately(client, login, satrack):
    headers = login()
    _, job = connect_account(client, headers, satrack)
    first = client.post("/api/viajes", json=trip_body(), headers=headers).json()
    client.post(f"/api/viajes/{first['id']}/transiciones", json={"estado": "cancelado", "motivo": "Prueba"}, headers=headers)
    send_callback(client, job["job_id"], "vehicles", vehicles=[{"plate": "ABC123"}])
    second = client.post("/api/viajes", json=trip_body(manifiesto="MAN-2"), headers=headers)
    assert second.status_code == 201
    assert second.json()["estado"] == "programado"
    assert len(satrack.jobs) == 1


def test_new_trip_with_unknown_plate_requests_verification(client, login, satrack):
    headers = login()
    _, job = connect_account(client, headers, satrack)
    send_callback(client, job["job_id"], "vehicles", vehicles=[])
    trip = client.post("/api/viajes", json=trip_body(), headers=headers).json()
    assert trip["estado"] == "registrado"
    assert len(satrack.jobs) == 2 and satrack.jobs[-1]["type"] == "vehicles"


def test_positions_feed_history_and_last_location(client, login, satrack):
    headers = login()
    _, job = connect_account(client, headers, satrack)
    trip = client.post("/api/viajes", json=trip_body(departure_in_h=0.5), headers=headers).json()
    send_callback(client, job["job_id"], "vehicles", vehicles=[{"plate": "ABC123"}])
    client.post(f"/api/viajes/{trip['id']}/transiciones", json={"estado": "en_ruta"}, headers=headers)
    assert client.post("/api/cuenta-satelital/consultar", headers=headers).status_code == 202
    positions_job = satrack.jobs[-1]
    assert positions_job["type"] == "positions" and positions_job["plates"] == ["ABC123"]
    row = {"plate": "ABC123", "lat": 6.13, "lng": -75.25, "speed_kmh": 35, "status": "En movimiento",
           "address": "Vía El Retiro", "reported_at": datetime.now(UTC).isoformat(), "reported_at_raw": "Hoy"}
    assert send_callback(client, positions_job["job_id"], "positions", positions=[row]).json() == {"status": "ok"}
    assert send_callback(client, positions_job["job_id"], "positions", positions=[row]).json()["duplicado"] is True
    history = client.get(f"/api/viajes/{trip['id']}/posiciones", headers=headers).json()
    assert len(history) == 1 and history[0]["direccion"] == "Vía El Retiro"
    vehicle = client.get("/api/vehiculos", headers=headers).json()["items"][0]
    assert vehicle["ultima_posicion"]["lat"] == 6.13


def test_callback_with_invalid_signature_is_rejected(client, login, satrack):
    _, job = connect_account(client, login(), satrack)
    assert send_callback(client, job["job_id"], "vehicles", secret="otra-clave-cualquiera").status_code == 401


def test_replayed_callback_outside_the_window_is_rejected(client, login, satrack):
    _, job = connect_account(client, login(), satrack)
    assert send_callback(client, job["job_id"], "vehicles", sent_at=time.time() - 600).status_code == 401


def test_malformed_callback_headers_are_rejected_without_server_errors(client, login, satrack):
    _, job = connect_account(client, login(), satrack)
    now = str(int(time.time())).encode()
    for timestamp, signature in ((b"\xb2", b"sha256=x"), (b"1" * 5000, b"sha256=x"), (now, b"sha256=\xf1")):
        response = client.post("/internal/satrack/callback", content=b"{}",
                               headers={"X-Timestamp": timestamp, "X-Signature": signature, "X-Job-Id": job["job_id"]})
        assert response.status_code == 401


def test_uncertain_post_stays_pending_until_timeout(app, client, login, satrack):
    satrack.available = False
    account = client.put("/api/cuenta-satelital", json=ACCOUNT, headers=login()).json()
    assert account["fallos_consecutivos"] == 0
    assert account["consulta_pendiente"]
    with app.state.sessions() as db:
        db.execute(update(ConsultaSatelital).values(enviado_en=datetime.now(UTC) - timedelta(minutes=10)))
        db.commit()
    for _ in range(2):
        asyncio.run(servicio.reconcile_queries(app.state.sessions, app.state.settings, satrack))
    with app.state.sessions() as db:
        assert db.scalar(select(CuentaSatelital.fallos_consecutivos)) == 1
        assert db.scalar(select(ConsultaSatelital.estado)) == "timeout"


def test_scheduled_task_runs_without_the_http_layer(app, client, login, satrack):
    headers = login()
    _, job = connect_account(client, headers, satrack)
    send_callback(client, job["job_id"], "vehicles", status="failed", errors=[{"code": "TIMEOUT", "message": "lento"}])
    state = app.state
    with state.sessions() as db:  # la consulta anterior ya superó la frecuencia de la transportadora (5 min)
        db.execute(update(ConsultaSatelital).values(enviado_en=datetime.now(UTC) - timedelta(minutes=10)))
        db.commit()
    asyncio.run(servicio.scheduled_queries(state.sessions, state.settings, satrack))
    assert len(satrack.jobs) == 2 and satrack.jobs[-1]["type"] == "vehicles"


def test_rotating_the_encryption_key_keeps_credentials_readable(app, client, login, satrack, settings):
    connect_account(client, login(), satrack)
    new_key = Fernet.generate_key().decode()
    rotated = settings.model_copy(update={"encryption_keys": new_key})
    with app.state.sessions() as db:
        assert servicio.reencrypt_accounts(db, rotated) == 1
        stored = db.scalar(select(CuentaSatelital.password_cifrado))
    assert Fernet(new_key).decrypt(stored.encode()) == b"clave-satrack"
