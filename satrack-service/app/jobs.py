import asyncio
import logging
import time
from datetime import datetime, timezone
from fastapi import HTTPException
from app.callback import send_callback
from app.errors import ProviderError
from app.schemas import CallbackPayload, JobError, JobStatus

logger = logging.getLogger(__name__)

JOB_RETENTION_S = 3600


class JobManager:
    def __init__(self, settings, provider, deliver=None):
        self.settings, self.provider = settings, provider
        if deliver:
            self.deliver = deliver
        elif settings.callback_url:
            self.deliver = lambda payload: send_callback(payload, settings)
        else:
            self.deliver = None
        self.semaphore = asyncio.Semaphore(settings.max_concurrency)
        self.locks = {}
        self.references = {}
        self.seen = {}
        self.statuses = {}
        self.tasks = set()
        self.running = 0
        self.queued = 0
        self.closing = False

    def prune(self):
        now = time.monotonic()
        self.seen = {key: until for key, until in self.seen.items() if until > now}
        self.statuses = {key: status for key, status in self.statuses.items()
                         if key in self.seen or status.status != "done" or status.callback == "pending"}

    def submit(self, job):
        now = time.monotonic()
        self.prune()
        key = str(job.job_id)
        if key in self.seen or key in self.statuses:
            raise HTTPException(409, "El job ya fue recibido")
        if self.closing or len(self.tasks) >= self.settings.max_queued_jobs + self.settings.max_concurrency:
            raise HTTPException(503, "La cola está llena; reintenta más tarde")
        if len(self.statuses) >= self.settings.max_retained_jobs:
            finished = next((key for key, status in self.statuses.items()
                             if status.status == "done" and status.callback != "pending"), None)
            if finished is None:
                raise HTTPException(503, "La cola está llena; reintenta más tarde")
            self.statuses.pop(finished)
        self.seen[key] = now + JOB_RETENTION_S
        self.statuses[key] = JobStatus(job_id=job.job_id, type=job.type, status="queued",
                                       received_at=datetime.now(timezone.utc),
                                       callback="pending" if self.deliver else "disabled")
        self.queued += 1
        self.locks.setdefault(job.account.id, asyncio.Lock())
        self.references[job.account.id] = self.references.get(job.account.id, 0) + 1
        task = asyncio.create_task(self.execute(job))
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)

    async def collect(self, job, state):
        lock = self.locks[job.account.id]
        async with lock:
            async with self.semaphore:
                self.queued -= 1
                self.running += 1
                state["started"] = True
                status = self.statuses.get(str(job.job_id))
                if status:
                    status.status, status.started_at = "running", datetime.now(timezone.utc)
                try:
                    if job.type == "vehicles":
                        return [], await asyncio.to_thread(self.provider.list_vehicles, job.account), []
                    all_positions = await asyncio.to_thread(self.provider.fetch_positions, job.account)
                    by_plate = {p.plate: p for p in all_positions}
                    positions, errors = [], []
                    for plate in job.plates:
                        position = by_plate.get(plate)
                        if position is None:
                            errors.append(JobError(plate=plate, code="VEHICLE_NOT_FOUND", message="La placa no está en la cuenta"))
                        else:
                            positions.append(position)
                            if position.lat is None or position.lng is None:
                                errors.append(JobError(plate=plate, code="POSITION_UNAVAILABLE", message="Ubicación no disponible en Satrack"))
                    return positions, [], errors
                except asyncio.CancelledError:
                    await asyncio.to_thread(self.provider.cancel, job.account.id)
                    raise
                finally:
                    self.running -= 1

    async def execute(self, job):
        payload = CallbackPayload(job_id=job.job_id, type=job.type, status="ok", finished_at=datetime.now(timezone.utc))
        state = {"started": False}
        try:
            payload.positions, payload.vehicles, payload.errors = await asyncio.wait_for(self.collect(job, state), self.settings.job_timeout_s)
            payload.status = "partial" if payload.errors else "ok"
        except TimeoutError:
            payload.status = "failed"
            payload.errors = [JobError(code="TIMEOUT", message="La consulta excedió el tiempo permitido")]
        except ProviderError as exc:
            payload.status = "failed"
            payload.errors = [JobError(code=exc.code, message=exc.message)]
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.error("Error del proveedor job=%s", job.job_id)
            payload.status = "failed"
            payload.errors = [JobError(code="PROVIDER_UNAVAILABLE", message="No fue posible consultar Satrack")]
        finally:
            if not state["started"]:
                self.queued -= 1
            self.references[job.account.id] -= 1
            if not self.references[job.account.id]:
                self.references.pop(job.account.id)
                self.locks.pop(job.account.id)
        payload.finished_at = datetime.now(timezone.utc)
        status = self.statuses.get(str(job.job_id))
        if status:
            status.status, status.result = "done", payload
        self.seen[str(job.job_id)] = time.monotonic() + JOB_RETENTION_S
        logger.info("Job terminado job=%s cuenta=%s tipo=%s estado=%s posiciones=%s vehiculos=%s errores=%s",
                    job.job_id, job.account.id, job.type, payload.status, len(payload.positions),
                    len(payload.vehicles), [e.code for e in payload.errors])
        if self.deliver:
            try:
                delivered = await self.deliver(payload)
                if status:
                    status.callback = "failed" if delivered is False else "delivered"
            except Exception:
                if status:
                    status.callback = "failed"
                logger.error("Callback no entregado job=%s", job.job_id)

    def status(self, job_id):
        self.prune()
        return self.statuses.get(str(job_id))

    async def close(self):
        self.closing = True
        for task in list(self.tasks):
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        await asyncio.to_thread(self.provider.close)
