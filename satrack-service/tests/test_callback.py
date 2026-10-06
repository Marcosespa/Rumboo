import hashlib
import hmac
import uuid
from datetime import datetime, timezone

import httpx

from app.callback import send_callback
from app.schemas import CallbackPayload
from tests.conftest import make_settings


def payload():
    return CallbackPayload(job_id=uuid.uuid4(), type="positions", status="ok", finished_at=datetime.now(timezone.utc))


async def test_firma_hmac_y_reintentos_hasta_exito():
    settings = make_settings(callback_url="http://api/internal/satrack/callback")
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(500 if len(calls) < 3 else 200)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        assert await send_callback(payload(), settings, client=client, delays=(0, 0, 0))

    assert len(calls) == 3
    request = calls[-1]
    expected = hmac.new(settings.callback_secret.encode(), request.content, hashlib.sha256).hexdigest()
    assert request.headers["X-Signature"] == f"sha256={expected}"


async def test_se_descarta_tras_agotar_reintentos():
    settings = make_settings(callback_url="http://api/internal/satrack/callback")
    transport = httpx.MockTransport(lambda request: httpx.Response(503))
    async with httpx.AsyncClient(transport=transport) as client:
        assert not await send_callback(payload(), settings, client=client, delays=(0, 0, 0))
