import asyncio
import logging
import secrets
from contextlib import asynccontextmanager
from uuid import UUID
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.config import Settings
from app.jobs import JobManager
from app.providers import get_provider
from app.schemas import JobRequest, JobStatus

logging.basicConfig(level=logging.INFO)


def create_app(settings=None, provider=None, deliver=None):
    settings = settings or Settings()
    manager = JobManager(settings, provider or get_provider(settings), deliver)

    @asynccontextmanager
    async def lifespan(app):
        async def cleanup():
            while True:
                await asyncio.sleep(60)
                manager.prune()
                if hasattr(manager.provider, "cleanup"):
                    await asyncio.to_thread(manager.provider.cleanup)
        task = asyncio.create_task(cleanup())
        try:
            yield
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
            await manager.close()

    app = FastAPI(title="Rumboo · Scraper Satrack", version="0.1.0", lifespan=lifespan)
    app.state.manager = manager

    def require_api_key(x_api_key: str = Header(default="")):
        if not secrets.compare_digest(x_api_key.encode(), settings.satrack_service_api_key.encode()):
            raise HTTPException(401, "API key inválida")

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        # Nunca se devuelve `input`: el body trae la contraseña de Satrack.
        errores = [{"campo": ".".join(str(p) for p in e["loc"] if p != "body") or "body",
                    "mensaje": str(e["msg"]).removeprefix("Value error, ")} for e in exc.errors()]
        return JSONResponse(status_code=422, content={"detail": "Payload inválido", "errores": errores})

    @app.get("/health")
    def health():
        return {"status": "ok", "provider": manager.provider.name, "running_jobs": manager.running,
                "queued_jobs": manager.queued,
                "sessions": manager.provider.session_count}

    @app.post("/v1/jobs", status_code=202, dependencies=[Depends(require_api_key)])
    async def jobs(job: JobRequest):
        manager.submit(job)
        return {"job_id": str(job.job_id)}

    @app.get("/v1/jobs/{job_id}", response_model=JobStatus, dependencies=[Depends(require_api_key)])
    async def job_status(job_id: UUID):
        status = manager.status(job_id)
        if status is None:
            raise HTTPException(404, "Job no encontrado o expirado (se guardan 1 h)")
        return status

    return app
