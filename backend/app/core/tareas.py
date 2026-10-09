"""Runner independiente de FastAPI y del negocio; liderazgo en PostgreSQL."""
import asyncio
import logging
import threading
from dataclasses import dataclass
from typing import Awaitable, Callable
from sqlalchemy import text
from app.core.db import now

logger = logging.getLogger(__name__)
LOCK_ID = 7_201_001


@dataclass(frozen=True)
class TareaPeriodica:
    nombre: str
    intervalo_s: float
    ejecutar: Callable[[], Awaitable[None]]

    def __post_init__(self):
        if self.intervalo_s <= 0:
            raise ValueError("El intervalo debe ser positivo")


class Runner:
    def __init__(self, engine, tareas, espera_lock_s=5, check_lock_s=1):
        self.engine = engine
        self.tareas = tuple(tareas)
        if len({t.nombre for t in self.tareas}) != len(self.tareas):
            raise ValueError("Los nombres de las tareas deben ser únicos")
        self.espera_lock_s = espera_lock_s
        self.check_lock_s = check_lock_s
        self.activo = False
        self._estado = {t.nombre: {"ultimo_intento": None, "ultimo_exito": None, "error": None} for t in self.tareas}
        self._conexion = None
        self._mutex = threading.Lock()

    def estado(self):
        return {"activo": self.activo,
                "ultimo_ciclo": {k: v["ultimo_intento"] for k, v in self._estado.items() if v["ultimo_intento"]},
                "tareas": {k: dict(v) for k, v in self._estado.items()}}

    async def ejecutar(self):
        while True:
            children = []
            try:
                acquisition = asyncio.create_task(asyncio.to_thread(self._tomar_lock))
                try:
                    acquired = await asyncio.shield(acquisition)
                except asyncio.CancelledError:
                    # to_thread sigue ejecutándose: esperar evita adquirir el lock después de soltarlo.
                    await acquisition
                    raise
                if not acquired:
                    await asyncio.sleep(self.espera_lock_s)
                    continue
                self.activo = True
                children = [asyncio.create_task(self._ciclo(t)) for t in self.tareas]
                monitor = asyncio.create_task(self._vigilar_lock())
                children.append(monitor)
                await monitor
            finally:
                self.activo = False
                for task in children:
                    task.cancel()
                await asyncio.gather(*children, return_exceptions=True)
                await asyncio.to_thread(self._soltar_lock)
            await asyncio.sleep(self.espera_lock_s)

    async def _vigilar_lock(self):
        while True:
            await asyncio.sleep(self.check_lock_s)
            if not await asyncio.to_thread(self._lock_vigente):
                self.activo = False
                logger.warning("Runner perdió el liderazgo; detiene tareas y recuperará la conexión")
                return

    async def _ciclo(self, tarea):
        while self.activo:
            self._estado[tarea.nombre]["ultimo_intento"] = now()
            try:
                await tarea.ejecutar()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self._estado[tarea.nombre]["error"] = type(exc).__name__
                logger.error("Falló la tarea %s; se reintentará", tarea.nombre)
            else:
                self._estado[tarea.nombre]["ultimo_exito"] = now()
                self._estado[tarea.nombre]["error"] = None
            await asyncio.sleep(tarea.intervalo_s)

    def _tomar_lock(self):
        with self._mutex:
            if self.engine.dialect.name != "postgresql":
                return True
            connection = None
            try:
                connection = self.engine.connect()
                if connection.scalar(text("SELECT pg_try_advisory_lock(:id)"), {"id": LOCK_ID}):
                    connection.commit()
                    self._conexion = connection
                    return True
                connection.close()
            except Exception:
                if connection is not None:
                    connection.invalidate()
                    connection.close()
                logger.error("Runner no pudo adquirir liderazgo")
            return False

    def _lock_vigente(self):
        with self._mutex:
            if self.engine.dialect.name != "postgresql":
                return True
            if self._conexion is None:
                return False
            try:
                self._conexion.execute(text("SET LOCAL statement_timeout = '2s'"))
                valid = self._conexion.scalar(text("""SELECT EXISTS (
                    SELECT 1 FROM pg_locks WHERE pid = pg_backend_pid() AND locktype = 'advisory'
                    AND classid = 0 AND objid = :id AND objsubid = 1 AND granted)"""), {"id": LOCK_ID})
                self._conexion.commit()
                return bool(valid)
            except Exception:
                self._conexion.invalidate()
                return False

    def _soltar_lock(self):
        with self._mutex:
            if self._conexion is None:
                return
            try:
                self._conexion.execute(text("SELECT pg_advisory_unlock(:id)"), {"id": LOCK_ID})
                self._conexion.commit()
            except Exception:
                self._conexion.invalidate()
            finally:
                self._conexion.close()
                self._conexion = None
