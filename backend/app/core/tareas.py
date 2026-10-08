import asyncio
import logging
from app.services.monitoreo import tick
from app.services.satrack_client import dispatch

logger = logging.getLogger(__name__)


async def run_scheduler(app):
    while True:
        try:
            jobs = await asyncio.to_thread(tick, app.state.sessions, app.state.settings)
            for job in jobs:
                await dispatch(app, job)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.error("Falló un ciclo del scheduler; se reintentará")
        await asyncio.sleep(app.state.settings.scheduler_interval_s)
