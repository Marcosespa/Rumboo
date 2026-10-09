import time
from datetime import UTC, datetime
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from app.main import create_app
from app.operacion import servicio as operacion
from app.operacion.schemas import ViajeDTO
from app.satelital.models import ConsultaSatelital, Posicion
from app.satelital.schemas import JobState
from tests.ayudas import send_callback, trip_body
from tests.satelital.test_flujo_satrack import connect_account


def test_fleet_imports_all_vehicles_with_locations_and_keeps_unimportable_rows(client, login, satrack):
    headers = login()
    _, job = connect_account(client, headers, satrack)
    rows = [{"plate": "ABC123", "name": "Camión Uno", "device_id": "1", "address": "Bogotá", "lat": 4.6, "lng": -74.1},
            {"plate": "XYZ789", "name": "Camión Dos", "device_id": "2", "address": "Cali"},
            {"plate": "REMOLQUE", "name": "Para revisión"}]
    assert send_callback(client, job["job_id"], "vehicles", vehicles=rows).status_code == 200
    vehicles = client.get("/api/vehiculos", headers=headers).json()["items"]
    assert [v["placa"] for v in vehicles] == ["ABC123", "XYZ789"]
    assert vehicles[0]["alias"] == "Camión Uno" and vehicles[0]["ultima_posicion"]["direccion"] == "Bogotá"
    assert vehicles[1]["ultima_posicion"]["direccion"] == "Cali"
    result = client.get(f"/api/consultas-satelitales/{job['job_id']}", headers=headers).json()
    assert result["estado"] == "ok" and len(result["resultado"]["vehicles"]) == 3
    partial = client.post("/api/cuenta-satelital/sincronizar", headers=headers).json()
    assert send_callback(client, partial["job_id"], "vehicles", status="partial", vehicles=[rows[0]]).status_code == 200
    assert all(v["en_satelital"] for v in client.get("/api/vehiculos", headers=headers).json()["items"])
    other = login("Otra Empresa", "otro")
    assert client.get("/api/vehiculos", headers=other).json()["items"] == []
    assert client.get(f"/api/consultas-satelitales/{job['job_id']}", headers=other).status_code == 404
    assert client.get(f"/api/consultas-satelitales/{job['job_id']}").status_code == 401


def test_restart_recovers_job_automatically_without_callback_or_http_followup(app, client, login, satrack, engine, settings):
    headers = login()
    _, job = connect_account(client, headers, satrack)
    satrack.states[job["job_id"]] = JobState.model_validate({"job_id": job["job_id"], "type": "vehicles", "status": "done",
        "result": {"job_id": job["job_id"], "type": "vehicles", "status": "ok", "finished_at": datetime.now(UTC),
                   "vehicles": [{"plate": "ABC123", "address": "Bogotá", "password": "no persistir"}]}})
    restarted = create_app(settings.model_copy(update={"scheduler_enabled": True, "runner_lock_check_s": 0.05}), engine, satrack)
    with TestClient(restarted) as recovered:
        deadline = time.monotonic() + 4
        while time.monotonic() < deadline:
            with restarted.state.sessions() as db:
                if db.get(ConsultaSatelital, job["job_id"]).estado == "ok":
                    break
            time.sleep(0.05)
        else:
            raise AssertionError("El runner no recuperó la consulta tras el reinicio")
        result = recovered.get(f"/api/consultas-satelitales/{job['job_id']}", headers=headers).json()
        assert "no persistir" not in str(result)
        assert recovered.get("/api/vehiculos", headers=headers).json()["items"][0]["ultima_posicion"]["direccion"] == "Bogotá"
        health = recovered.get("/health").json()
        assert health["tareas"]["activo"]
        assert health["tareas"]["tareas"]["satelital.reconciliar"]["ultimo_exito"]
    assert len(satrack.jobs) == 1
    # Callback posterior al GET: mismo efecto, sin posición duplicada.
    assert send_callback(client, job["job_id"], "vehicles", vehicles=[{"plate": "ABC123"}]).json()["duplicado"]
    with app.state.sessions() as db:
        assert db.scalar(select(func.count()).select_from(Posicion)) == 1


def test_late_position_belongs_to_requested_trip_not_current_trip(app, client, login, satrack):
    headers = login()
    _, fleet = connect_account(client, headers, satrack)
    old = client.post("/api/viajes", json=trip_body(departure_in_h=0.5), headers=headers).json()
    send_callback(client, fleet["job_id"], "vehicles", vehicles=[{"plate": "ABC123"}])
    position_job = client.post("/api/cuenta-satelital/consultar", headers=headers).json()
    assert position_job["status"] == "aceptado"
    pending = client.post("/api/cuenta-satelital/consultar", headers=headers).json()
    assert pending["status"] == "pendiente" and pending["job_id"] == position_job["job_id"]
    client.post(f"/api/viajes/{old['id']}/transiciones", json={"estado": "cancelado", "motivo": "Cambio"}, headers=headers)
    new = client.post("/api/viajes", json=trip_body(manifiesto="MAN-2", departure_in_h=0.5), headers=headers).json()
    row = {"plate": "ABC123", "lat": 4.6, "lng": -74.1, "reported_at": datetime.now(UTC).isoformat()}
    assert send_callback(client, position_job["job_id"], "positions", positions=[row]).status_code == 200
    assert len(client.get(f"/api/viajes/{old['id']}/posiciones", headers=headers).json()) == 1
    assert client.get(f"/api/viajes/{new['id']}/posiciones", headers=headers).json() == []
    with app.state.sessions() as db:
        dto = operacion.get_trip(db, 1, new["id"])
    assert isinstance(dto, ViajeDTO) and dto.vehiculo.placa == "ABC123"
    assert app.state.consultas is not create_app(app.state.settings, app.state.engine, satrack).state.consultas


def test_old_credentials_callback_cannot_import_into_new_account(client, login, satrack):
    headers = login()
    _, previous = connect_account(client, headers, satrack)
    _, current = connect_account(client, headers, satrack)
    assert send_callback(client, previous["job_id"], "vehicles", vehicles=[{"plate": "ABC123"}]).json()["obsoleto"]
    assert client.get("/api/vehiculos", headers=headers).json()["items"] == []
    assert send_callback(client, current["job_id"], "vehicles", vehicles=[{"plate": "XYZ789"}]).status_code == 200
    assert [v["placa"] for v in client.get("/api/vehiculos", headers=headers).json()["items"]] == ["XYZ789"]


def test_unknown_job_retries_same_uuid_but_running_job_is_not_resent(app, client, login, satrack):
    import asyncio
    from datetime import timedelta
    from sqlalchemy import update
    from app.core.db import now
    from app.satelital import servicio
    from app.satelital.cliente import ServicioSatelitalNoDisponible
    original_send = satrack.send_job

    async def ambiguous_send(job):
        await original_send(job)
        raise ServicioSatelitalNoDisponible()
    satrack.send_job = ambiguous_send
    headers = login()
    _, job = connect_account(client, headers, satrack)
    with app.state.sessions() as db:
        db.execute(update(ConsultaSatelital).values(proximo_envio=now() - timedelta(seconds=1)))
        db.commit()
    asyncio.run(servicio.reconcile_queries(app.state.sessions, app.state.settings, satrack))
    assert len(satrack.jobs) == 1
    satrack.states.pop(job["job_id"])
    satrack.send_job = original_send
    asyncio.run(servicio.reconcile_queries(app.state.sessions, app.state.settings, satrack))
    assert len(satrack.jobs) == 2 and satrack.jobs[0]["job_id"] == satrack.jobs[1]["job_id"]
    with app.state.sessions() as db:
        assert db.get(ConsultaSatelital, job["job_id"]).estado == "pendiente"


def test_bad_polled_result_does_not_block_another_company(app, client, login, satrack):
    import asyncio
    from app.satelital import servicio
    first = login()
    _, first_job = connect_account(client, first, satrack)
    second = login("Otra Empresa", "otro")
    _, second_job = connect_account(client, second, satrack)
    for job, kind in ((first_job, "positions"), (second_job, "vehicles")):
        satrack.states[job["job_id"]] = JobState.model_validate({"job_id": job["job_id"], "type": kind, "status": "done",
            "result": {"job_id": job["job_id"], "type": kind, "status": "ok", "finished_at": datetime.now(UTC),
                       "vehicles": [{"plate": "XYZ789"}]}})
    asyncio.run(servicio.reconcile_queries(app.state.sessions, app.state.settings, satrack))
    assert client.get(f"/api/consultas-satelitales/{first_job['job_id']}", headers=first).json()["error_codigo"] == "INVALID_RESULT"
    assert client.get("/api/vehiculos", headers=first).json()["items"] == []
    assert client.get("/api/vehiculos", headers=second).json()["items"][0]["placa"] == "XYZ789"


def test_oversized_callback_is_rejected_before_validation(client):
    response = client.post("/internal/satrack/callback", content=b"x" * 2_000_001,
                           headers={"X-Timestamp": str(int(time.time()))})
    assert response.status_code == 413
