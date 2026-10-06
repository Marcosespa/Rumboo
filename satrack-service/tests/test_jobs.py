import threading
import time

from app.providers.simulator import SimulatorProvider
from app.schemas import Position
from tests.conftest import job_body, make_settings, wait_done


class SlowProvider(SimulatorProvider):
    """Registra cuántas consultas corren a la vez y cuáles se cancelaron."""

    def __init__(self, delay):
        self.delay, self.active, self.max_active, self.cancelled = delay, 0, 0, []
        self.lock = threading.Lock()

    def fetch_positions(self, account):
        with self.lock:
            self.active += 1
            self.max_active = max(self.max_active, self.active)
        try:
            time.sleep(self.delay)
            return [Position(plate="ABC123", lat=4.6, lng=-74.0)]
        finally:
            with self.lock:
                self.active -= 1

    def cancel(self, account_id):
        self.cancelled.append(account_id)


async def test_timeout_responde_timeout_y_cancela_la_sesion(client_factory):
    provider = SlowProvider(delay=1)
    client = await client_factory(settings=make_settings(job_timeout_s=0.2), provider=provider)
    body = job_body()
    await client.post("/v1/jobs", json=body)
    result = (await wait_done(client, body["job_id"]))["result"]
    assert result["errors"][0]["code"] == "TIMEOUT"
    assert provider.cancelled == ["12"]


async def test_jobs_de_la_misma_cuenta_no_corren_a_la_vez(client_factory):
    provider = SlowProvider(delay=0.1)
    client = await client_factory(provider=provider)
    bodies = [job_body() for _ in range(3)]
    for body in bodies:
        await client.post("/v1/jobs", json=body)
    for body in bodies:
        await wait_done(client, body["job_id"])
    assert provider.max_active == 1


async def test_jobs_de_cuentas_distintas_corren_en_paralelo(client_factory):
    provider = SlowProvider(delay=0.2)
    client = await client_factory(provider=provider)
    bodies = [job_body(account_id=str(i)) for i in range(3)]
    for body in bodies:
        await client.post("/v1/jobs", json=body)
    for body in bodies:
        await wait_done(client, body["job_id"])
    assert provider.max_active > 1


async def test_cola_llena_responde_503(client_factory):
    provider = SlowProvider(delay=0.5)
    client = await client_factory(settings=make_settings(max_concurrency=1, max_queued_jobs=1), provider=provider)
    codes = [(await client.post("/v1/jobs", json=job_body(account_id=str(i)))).status_code for i in range(3)]
    assert codes == [202, 202, 503]


async def test_callback_recibe_el_resultado(client_factory):
    received = []

    async def deliver(payload):
        received.append(payload)
        return True

    client = await client_factory(deliver=deliver)
    body = job_body()
    await client.post("/v1/jobs", json=body)
    status = await wait_done(client, body["job_id"])
    assert status["callback"] == "delivered"
    assert str(received[0].job_id) == body["job_id"]
