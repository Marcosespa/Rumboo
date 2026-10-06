import asyncio
import logging
import threading
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from app.config import Settings
from app.db import make_engine
from app.routers import auth, cuenta_satelital, flota, internal, panel, viajes
from app.scheduler import run_scheduler

logging.basicConfig(level=logging.INFO)


def create_app(settings=None, engine=None):
    settings = settings or Settings()
    engine = engine or make_engine(settings.database_url)

    @asynccontextmanager
    async def lifespan(app):
        app.state.http = httpx.AsyncClient(timeout=10)
        scheduler = asyncio.create_task(run_scheduler(app)) if settings.scheduler_enabled else None
        yield
        if scheduler:
            scheduler.cancel()
            await asyncio.gather(scheduler, return_exceptions=True)
        await app.state.http.aclose()
        engine.dispose()

    app = FastAPI(title="Rumboo · API operativa", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.engine = engine
    app.state.sessions = sessionmaker(engine, expire_on_commit=False)
    app.state.login_attempts = {}
    app.state.login_lock = threading.Lock()
    app.add_middleware(CORSMiddleware, allow_origins=[v.strip() for v in settings.cors_origins.split(",") if v.strip()],
                       allow_methods=["GET", "POST", "PUT"], allow_headers=["Authorization", "Content-Type"])
    for router in (auth.router, viajes.router, flota.router, cuenta_satelital.router, panel.router, internal.router):
        app.include_router(router)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        # Do not return input values: validation may include passwords.
        fields = [{"campo": ".".join(str(p) for p in error["loc"] if p != "body"),
                   "mensaje": error["msg"].replace("Value error, ", "")} for error in exc.errors()]
        return JSONResponse(status_code=422, content={"detail": "Revisa los campos del formulario", "errores": fields})

    @app.exception_handler(IntegrityError)
    async def conflict(request, exc):
        return JSONResponse(status_code=409, content={"detail": "El registro ya existe o entra en conflicto con otro viaje activo"})

    @app.exception_handler(Exception)
    async def unexpected(request, exc):
        logging.getLogger(__name__).error("Error no esperado ruta=%s tipo=%s", request.url.path, type(exc).__name__)
        return JSONResponse(status_code=500, content={"detail": "No fue posible completar la operación; vuelve a intentar"})

    @app.get("/health", tags=["Estado"])
    def health():
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError:
            raise HTTPException(503, "La base de datos no está disponible")
        return {"status": "ok", "database": "ok", "scheduler": settings.scheduler_enabled}

    return app
