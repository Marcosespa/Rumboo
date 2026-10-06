import logging
import httpx
from sqlalchemy import select
from app.db import now
from app.models import ConsultaSatelital, CuentaSatelital

logger = logging.getLogger(__name__)


async def dispatch(app, job):
    if not job:
        return
    try:
        response = await app.state.http.post(app.state.settings.satrack_service_url + "/v1/jobs", json=job,
            headers={"X-Api-Key": app.state.settings.satrack_service_api_key})
        if response.status_code not in (202, 409):
            response.raise_for_status()
    except httpx.HTTPError:
        with app.state.sessions() as db:
            query = db.scalar(select(ConsultaSatelital).where(ConsultaSatelital.job_id == job["job_id"]).with_for_update())
            if query and query.estado == "pendiente" and query.respondido_en is None:
                query.estado = "fallido"
                query.error_codigo = "SERVICE_UNAVAILABLE"
                query.error_detalle = "El servicio satelital no está disponible; se reintentará"
                account = db.get(CuentaSatelital, query.cuenta_satelital_id)
                if account.version == query.cuenta_version:
                    account.fallos_consecutivos += 1
                    account.ultimo_error = query.error_detalle
                    if account.fallos_consecutivos >= 3:
                        account.estado = "falla"
                db.commit()
        logger.warning("Servicio satelital no disponible job=%s", job["job_id"])
