import asyncio
from datetime import UTC, datetime, timedelta
from sqlalchemy import event, func, select, update
from app.core.db import now
from app.satelital import servicio
from app.satelital.models import ConsultaSatelital, CuentaSatelital, Posicion
from app.satelital.schemas import JobState
from tests.ayudas import send_callback
from tests.satelital.test_flujo_satrack import connect_account


def done(job_id, kind="vehicles", **result):
    return JobState.model_validate({"job_id": job_id, "type": kind, "status": "done", "result": {
        "job_id": job_id, "type": kind, "status": "ok", "finished_at": datetime.now(UTC), **result}})


def age_queries(app, minutes=10):
    with app.state.sessions() as db:
        db.execute(update(ConsultaSatelital).values(enviado_en=now() - timedelta(minutes=minutes)))
        db.commit()


def reconcile(app, satrack):
    asyncio.run(servicio.reconcile_queries(app.state.sessions, app.state.settings, satrack))


def test_result_ready_in_scraper_survives_api_outage_longer_than_timeout(app, client, login, satrack):
    headers = login()
    _, job = connect_account(client, headers, satrack)
    satrack.states[job["job_id"]] = done(job["job_id"], vehicles=[{"plate": "ABC123", "address": "Bogotá"}])
    age_queries(app)  # la API estuvo detenida más que CONSULTA_TIMEOUT_S y no hubo callback
    reconcile(app, satrack)
    with app.state.sessions() as db:
        assert db.get(ConsultaSatelital, job["job_id"]).estado == "ok"
        assert db.scalar(select(CuentaSatelital.fallos_consecutivos)) == 0
    assert client.get("/api/vehiculos", headers=headers).json()["items"][0]["ultima_posicion"]["direccion"] == "Bogotá"


def test_running_job_past_deadline_times_out_once_and_late_result_only_adds_history(app, client, login, satrack):
    headers = login()
    _, fleet = connect_account(client, headers, satrack)
    earlier = (datetime.now(UTC) - timedelta(minutes=30)).isoformat()
    send_callback(client, fleet["job_id"], "vehicles", vehicles=[{"plate": "ABC123", "address": "Antes", "reported_at": earlier}])
    job = client.post("/api/cuenta-satelital/sincronizar", headers=headers).json()
    age_queries(app)
    for _ in range(2):  # el scraper sigue en "running": vence una vez y cuenta un solo fallo
        reconcile(app, satrack)
    with app.state.sessions() as db:
        assert db.get(ConsultaSatelital, job["job_id"]).estado == "timeout"
        assert db.scalar(select(CuentaSatelital.fallos_consecutivos)) == 1
    late = send_callback(client, job["job_id"], "vehicles", vehicles=[
        {"plate": "ABC123", "address": "Después", "reported_at": datetime.now(UTC).isoformat()}, {"plate": "XYZ789"}])
    assert late.json() == {"status": "ok", "tardio": True}
    assert send_callback(client, job["job_id"], "vehicles", vehicles=[]).json()["duplicado"]
    with app.state.sessions() as db:
        query = db.get(ConsultaSatelital, job["job_id"])
        assert query.estado == "timeout" and query.resultado is not None
        assert db.scalar(select(CuentaSatelital.fallos_consecutivos)) == 1
        assert db.scalar(select(func.count()).select_from(Posicion)) == 2
    vehicles = client.get("/api/vehiculos", headers=headers).json()["items"]
    assert [v["placa"] for v in vehicles] == ["ABC123"]
    assert vehicles[0]["ultima_posicion"]["direccion"] == "Antes"


def test_result_for_replaced_credentials_keeps_query_cancelled(client, login, satrack):
    headers = login()
    _, previous = connect_account(client, headers, satrack)
    connect_account(client, headers, satrack)
    assert send_callback(client, previous["job_id"], "vehicles", vehicles=[{"plate": "ABC123"}]).json()["obsoleto"]
    query = client.get(f"/api/consultas-satelitales/{previous['job_id']}", headers=headers).json()
    assert query["estado"] == "cancelado" and query["error_codigo"] == "STALE_ACCOUNT"


def test_router_and_runner_dispatching_the_same_job_send_it_once(app, client, login, satrack):
    satrack.available = False
    assert client.put("/api/cuenta-satelital", json={"usuario": "u", "password": "p"}, headers=login()).status_code == 200
    satrack.available = True
    with app.state.sessions() as db:
        db.execute(update(ConsultaSatelital).values(proximo_envio=now() - timedelta(seconds=1)))
        db.commit()
        job_id = db.scalar(select(ConsultaSatelital.job_id))

    async def both():
        args = (app.state.sessions, app.state.settings, satrack, job_id)
        await asyncio.gather(servicio.dispatch(*args), servicio.dispatch(*args))
    asyncio.run(both())
    assert [j["job_id"] for j in satrack.jobs] == [job_id]


def test_unreadable_credentials_fail_one_account_without_blocking_others(app, client, login, satrack):
    satrack.available = False
    first = login()
    assert client.put("/api/cuenta-satelital", json={"usuario": "a", "password": "p"}, headers=first).status_code == 200
    assert client.put("/api/cuenta-satelital", json={"usuario": "b", "password": "p"}, headers=login("Otra Empresa", "otro")).status_code == 200
    satrack.available = True
    with app.state.sessions() as db:
        broken = db.scalar(select(CuentaSatelital).order_by(CuentaSatelital.id))
        broken.password_cifrado = "token-que-ninguna-clave-descifra"
        db.execute(update(ConsultaSatelital).values(proximo_envio=now() - timedelta(seconds=1)))
        db.commit()
        broken_job = db.scalar(select(ConsultaSatelital.job_id).where(ConsultaSatelital.cuenta_satelital_id == broken.id))
    reconcile(app, satrack)  # el scraper no conoce ninguno de los dos: ambos se reenvían
    assert [j["account"]["username"] for j in satrack.jobs] == ["b"]
    with app.state.sessions() as db:
        assert db.get(ConsultaSatelital, broken_job).estado == "fallido"
        assert db.get(ConsultaSatelital, broken_job).error_codigo == "CREDENTIALS_UNREADABLE"
        assert db.get(CuentaSatelital, broken.id).estado == "credenciales_invalidas"


def test_fleet_result_cost_grows_linearly_without_loading_full_trips(app, client, login, satrack, engine):
    headers = login()
    _, job = connect_account(client, headers, satrack)
    rows = [{"plate": f"AAA{i:03d}", "address": "Bogotá", "reported_at": datetime.now(UTC).isoformat()} for i in range(60)]
    statements = []

    def count(*_):
        statements.append(1)
    event.listen(engine, "before_cursor_execute", count)
    try:
        assert send_callback(client, job["job_id"], "vehicles", vehicles=rows).status_code == 200
    finally:
        event.remove(engine, "before_cursor_execute", count)
    with app.state.sessions() as db:
        assert db.scalar(select(func.count()).select_from(Posicion)) == 60
    # Importar un vehículo nuevo cuesta ~11 sentencias; cargar el viaje completo por posición superaría la cota.
    assert len(statements) <= 60 * 12
