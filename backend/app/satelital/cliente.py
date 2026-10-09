"""Adaptador del contrato existente de satrack-service; sin conocimiento del negocio."""
import httpx
from pydantic import ValidationError
from app.satelital.schemas import JobState


class ServicioSatelitalNoDisponible(Exception):
    pass


class SatrackServiceClient:
    def __init__(self, base_url, api_key, timeout=10, http=None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.http = http or httpx.AsyncClient(timeout=timeout)

    async def send_job(self, job):
        try:
            response = await self.http.post(self.base_url + "/v1/jobs", json=job,
                                            headers={"X-Api-Key": self.api_key})
            if response.status_code not in (202, 409):
                raise ServicioSatelitalNoDisponible()
        except httpx.HTTPError as exc:
            raise ServicioSatelitalNoDisponible() from exc

    async def get_job(self, job_id):
        try:
            response = await self.http.get(self.base_url + f"/v1/jobs/{job_id}",
                                           headers={"X-Api-Key": self.api_key})
            if response.status_code == 404:
                return None
            response.raise_for_status()
            if len(response.content) > 2_000_000:
                raise ServicioSatelitalNoDisponible()
            state = JobState.model_validate_json(response.content)
            if str(state.job_id) != job_id or (state.result and (
                    str(state.result.job_id) != job_id or state.result.type != state.type)):
                raise ServicioSatelitalNoDisponible()
            return state
        except (httpx.HTTPError, ValidationError) as exc:
            raise ServicioSatelitalNoDisponible() from exc

    async def close(self):
        await self.http.aclose()
