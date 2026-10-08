"""Único archivo que conoce el contrato HTTP de satrack-service (POST /v1/jobs con X-Api-Key).

Si mañana se usa la API oficial de Satrack u otro proveedor, cambia este archivo y nada más.
"""
import httpx


class ServicioSatelitalNoDisponible(Exception):
    pass


class SatrackServiceClient:
    def __init__(self, base_url, api_key, timeout=10):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.http = httpx.AsyncClient(timeout=timeout)

    async def send_job(self, job):
        """202 aceptado o 409 ya recibido cuentan como entregado; cualquier otra respuesta es indisponibilidad."""
        try:
            response = await self.http.post(self.base_url + "/v1/jobs", json=job, headers={"X-Api-Key": self.api_key})
            if response.status_code not in (202, 409):
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ServicioSatelitalNoDisponible() from exc

    async def close(self):
        await self.http.aclose()
