"""Raíz de composición: el único lugar que conoce todos los módulos y los conecta entre sí.

Aquí se registran los routers, se enlazan suscripciones de eventos y extensiones (`<modulo>/enlaces.py`) y se
arma la lista de tareas de fondo. Los módulos nunca se conectan entre ellos por su cuenta.
"""
import asyncio
import logging
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from app import modelos  # noqa: F401  (registra todas las tablas)
from app.acceso.router import router as acceso_router
from app.core.config import Settings
from app.core.db import make_engine
from app.core.errores import ErrorDominio
from app.core.eventos import Bus
from app.core.tareas import Runner
from app.core.web import domain_error
from app.indicadores.router import router as indicadores_router
from app.operacion.router import router as operacion_router
from app.satelital import enlaces as satelital_enlaces
from app.satelital.cliente import SatrackServiceClient
from app.satelital.router import router as satelital_router

logging.basicConfig(level=logging.INFO)


def create_app(settings=None, engine=None, satrack=None):
    settings = settings or Settings()
    engine = engine or make_engine(settings.database_url)
    sessions = sessionmaker(engine, expire_on_commit=False)
    satrack = satrack or SatrackServiceClient(settings.satrack_service_url, settings.satrack_service_api_key)
    bus = Bus()
    satelital_enlaces.connect(bus, sessions, settings, satrack)
    runner = Runner(engine, satelital_enlaces.tasks(sessions, settings, satrack))

    @asynccontextmanager
    async def lifespan(app):
        task = asyncio.create_task(runner.ejecutar()) if settings.scheduler_enabled else None
        yield
        if task:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        await satrack.close()
        engine.dispose()

    app = FastAPI(title="Rumboo · API operativa", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.engine = engine
    app.state.sessions = sessions
    app.state.satrack = satrack
    app.state.eventos = bus
    app.state.tareas = runner
    app.state.login_attempts = {}
    app.state.login_lock = threading.Lock()
    app.add_middleware(CORSMiddleware, allow_origins=[v.strip() for v in settings.cors_origins.split(",") if v.strip()],
                       allow_methods=["GET", "POST", "PUT"], allow_headers=["Authorization", "Content-Type"])
    for router in (acceso_router, operacion_router, satelital_router, indicadores_router):
        app.include_router(router)
    app.add_exception_handler(ErrorDominio, domain_error)

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
        return {"status": "ok", "database": "ok", "scheduler": settings.scheduler_enabled, "tareas": runner.estado()}

    return app
