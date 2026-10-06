import asyncio
import hashlib
import hmac
import logging
import httpx
from app.schemas import CallbackPayload

logger = logging.getLogger(__name__)


async def send_callback(payload: CallbackPayload, settings, client=None, delays=(2, 10, 30)):
    body = payload.model_dump_json().encode()
    signature = hmac.new(settings.callback_secret.encode(), body, hashlib.sha256).hexdigest()
    headers = {"Content-Type": "application/json", "X-Job-Id": str(payload.job_id),
               "X-Signature": f"sha256={signature}"}
    owned = client is None
    client = client or httpx.AsyncClient(timeout=5)
    try:
        for attempt in range(len(delays) + 1):
            try:
                response = await client.post(settings.callback_url, content=body, headers=headers)
                response.raise_for_status()
                return True
            except httpx.HTTPError:
                logger.warning("Callback no entregado job=%s intento=%s", payload.job_id, attempt + 1)
                if attempt < len(delays):
                    await asyncio.sleep(delays[attempt])
        return False
    finally:
        if owned:
            await client.aclose()
