import asyncio
import uuid

import httpx
import pytest

from app.config import Settings
from app.main import create_app
from app.providers.simulator import SimulatorProvider

API_KEY = "test-api-key-0123456789"


def make_settings(**overrides):
    values = dict(satrack_service_api_key=API_KEY, callback_secret="test-callback-secret-0123",
                  callback_url="", provider="simulator", job_timeout_s=5)
    values.update(overrides)
    return Settings(_env_file=None, **values)


def job_body(type_="positions", plates=("ABC123",), password="clave", account_id="12"):
    return {"job_id": str(uuid.uuid4()), "type": type_,
            "account": {"id": account_id, "username": "usuario", "password": password},
            "plates": list(plates)}


@pytest.fixture
async def client_factory():
    """Crea un cliente HTTP contra la app con su lifespan activo."""
    stack = []

    async def factory(settings=None, provider=None, deliver=None):
        app = create_app(settings or make_settings(), provider or SimulatorProvider(), deliver)
        lifespan = app.router.lifespan_context(app)
        await lifespan.__aenter__()
        client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test",
                                   headers={"X-Api-Key": API_KEY})
        stack.append((lifespan, client))
        return client

    yield factory
    for lifespan, client in reversed(stack):
        await client.aclose()
        await lifespan.__aexit__(None, None, None)


async def wait_done(client, job_id, timeout=5):
    deadline = asyncio.get_running_loop().time() + timeout
    while True:
        response = await client.get(f"/v1/jobs/{job_id}")
        assert response.status_code == 200, response.text
        if response.json()["status"] == "done":
            return response.json()
        assert asyncio.get_running_loop().time() < deadline, "el job no terminó a tiempo"
        await asyncio.sleep(0.02)
