import asyncio
from datetime import UTC, datetime
from uuid import uuid4
import httpx
import pytest
from app.satelital.cliente import SatrackServiceClient, ServicioSatelitalNoDisponible


def test_adapter_uses_existing_contract_auth_and_distinguishes_unknown_job():
    job_id = str(uuid4())
    requests = []
    def respond(request):
        requests.append(request)
        if request.method == "POST":
            return httpx.Response(409)
        return httpx.Response(404)
    async def scenario():
        http = httpx.AsyncClient(transport=httpx.MockTransport(respond), timeout=10)
        adapter = SatrackServiceClient("http://satrack", "test-api-key", http=http)
        try:
            await adapter.send_job({"job_id": job_id, "type": "vehicles"})
            assert await adapter.get_job(job_id) is None
        finally:
            await adapter.close()
    asyncio.run(scenario())
    assert [r.url.path for r in requests] == ["/v1/jobs", f"/v1/jobs/{job_id}"]
    assert all(r.headers["X-Api-Key"] == "test-api-key" for r in requests)


@pytest.mark.parametrize("problem", ["different_job", "different_type", "invalid_payload", "server_error"])
def test_adapter_rejects_invalid_results_and_hides_response_details(problem):
    job_id = str(uuid4())
    payload = {"job_id": job_id, "type": "vehicles", "status": "done", "result": {
        "job_id": job_id, "type": "vehicles", "status": "ok", "finished_at": datetime.now(UTC).isoformat()}}
    if problem == "different_job":
        payload["result"]["job_id"] = str(uuid4())
    elif problem == "different_type":
        payload["result"]["type"] = "positions"
    elif problem == "invalid_payload":
        payload["result"]["status"] = "valor-invalido"
    def respond(request):
        return httpx.Response(503, text="no devolver") if problem == "server_error" else httpx.Response(200, json=payload)
    async def scenario():
        adapter = SatrackServiceClient("http://satrack", "test-api-key", http=httpx.AsyncClient(transport=httpx.MockTransport(respond)))
        try:
            with pytest.raises(ServicioSatelitalNoDisponible) as exc:
                await adapter.get_job(job_id)
            assert "no devolver" not in str(exc.value)
        finally:
            await adapter.close()
    asyncio.run(scenario())
