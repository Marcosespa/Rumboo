import asyncio
import time

from app.schemas import JobRequest
from app.jobs import JobManager
from app.providers.simulator import SimulatorProvider
from tests.conftest import job_body, make_settings, wait_done


async def test_vehicles_incluye_datos_satelitales_sin_credenciales(client_factory):
    client = await client_factory()
    body = job_body(type_="vehicles", plates=(), password="una-clave-privada")
    await client.post("/v1/jobs", json=body)
    status = await wait_done(client, body["job_id"])
    assert "una-clave-privada" not in str(status)
    vehicle = status["result"]["vehicles"][0]
    assert vehicle["lat"] is not None and vehicle["lng"] is not None
    assert vehicle["speed_kmh"] is not None
    assert vehicle["reported_at"].endswith("Z")


async def test_expiracion_se_aplica_tambien_al_consultar():
    manager = JobManager(make_settings(), SimulatorProvider())
    job = JobRequest.model_validate(job_body())
    manager.submit(job)
    await asyncio.gather(*manager.tasks)
    manager.seen[str(job.job_id)] = time.monotonic() - 1
    assert manager.status(job.job_id) is None
    await manager.close()


async def test_retencion_acotada_conserva_deduplicacion():
    manager = JobManager(make_settings(max_retained_jobs=1), SimulatorProvider())
    first, second = (JobRequest.model_validate(job_body()) for _ in range(2))
    manager.submit(first)
    await asyncio.gather(*manager.tasks)
    manager.submit(second)
    await asyncio.gather(*manager.tasks)
    assert manager.status(first.job_id) is None
    assert manager.status(second.job_id).result.status == "ok"
    assert len(manager.statuses) == 1
    assert str(first.job_id) in manager.seen
    await manager.close()


async def test_fallo_callback_no_pierde_resultado(client_factory):
    async def broken(payload):
        raise RuntimeError("conexión fallida")

    client = await client_factory(deliver=broken)
    body = job_body()
    await client.post("/v1/jobs", json=body)
    status = await wait_done(client, body["job_id"])
    assert status["result"]["status"] == "ok"
    assert status["callback"] == "failed"


def test_modo_independiente_no_requiere_callback_secret():
    assert make_settings(callback_secret="").callback_url == ""
