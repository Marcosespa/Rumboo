import hashlib
import hmac
from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import ValidationError
from app.deps import DB
from app.schemas import CallbackInput
from app.services.monitoreo import process_callback

router = APIRouter(tags=["Interno"])


@router.post("/internal/satrack/callback", include_in_schema=False)
async def callback(request: Request, db: DB, x_signature: str = Header(default=""), x_job_id: str = Header(default="")):
    body = await request.body()
    if len(body) > 2_000_000:
        raise HTTPException(413, "Respuesta demasiado grande")
    expected = "sha256=" + hmac.new(request.app.state.settings.callback_secret.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(x_signature, expected):
        raise HTTPException(401, "Firma del callback inválida")
    try:
        payload = CallbackInput.model_validate_json(body)
    except ValidationError:
        raise HTTPException(422, "El callback no cumple el contrato")
    if str(payload.job_id) != x_job_id:
        raise HTTPException(422, "El identificador del callback no coincide")
    return process_callback(db, payload)
