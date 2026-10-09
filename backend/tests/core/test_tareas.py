import asyncio
from app.core.tareas import Runner, TareaPeriodica


def test_runner_executes_tasks_without_fastapi(engine):
    calls = []

    async def task():
        calls.append(1)

    async def scenario():
        runner = Runner(engine, [TareaPeriodica("prueba", 0.01, task)])
        running = asyncio.create_task(runner.ejecutar())
        await asyncio.sleep(0.2)
        state = runner.estado()
        running.cancel()
        await asyncio.gather(running, return_exceptions=True)
        return state, runner.estado()

    during, after = asyncio.run(scenario())
    assert calls
    assert during["activo"] and "prueba" in during["ultimo_ciclo"]
    assert not after["activo"]


def test_only_one_runner_executes_at_a_time(engine):
    first_calls, second_calls = [], []

    async def first_task():
        first_calls.append(1)

    async def second_task():
        second_calls.append(1)

    async def scenario():
        first = Runner(engine, [TareaPeriodica("primero", 0.01, first_task)])
        second = Runner(engine, [TareaPeriodica("segundo", 0.01, second_task)], espera_lock_s=0.01)
        first_running = asyncio.create_task(first.ejecutar())
        await asyncio.sleep(0.2)
        second_running = asyncio.create_task(second.ejecutar())
        await asyncio.sleep(0.2)
        blocked = (second.activo, len(second_calls))
        first_running.cancel()
        await asyncio.gather(first_running, return_exceptions=True)
        await asyncio.sleep(0.3)
        took_over = second.activo and bool(second_calls)
        second_running.cancel()
        await asyncio.gather(second_running, return_exceptions=True)
        return blocked, took_over

    blocked, took_over = asyncio.run(scenario())
    assert first_calls
    assert blocked == (False, 0)
    assert took_over


def test_lost_postgres_connection_stops_leader_and_allows_takeover(engine):
    from sqlalchemy import text
    from app.core.tareas import LOCK_ID
    first_calls, second_calls = [], []

    async def first_task():
        first_calls.append(1)

    async def second_task():
        second_calls.append(1)

    async def wait_until(condition):
        # 5 s de margen: con la suite completa en paralelo, 1 s resultó intermitente.
        for _ in range(500):
            if condition():
                return
            await asyncio.sleep(0.01)
        raise AssertionError("No cambió el liderazgo")

    async def scenario():
        first = Runner(engine, [TareaPeriodica("primero", 0.01, first_task)], espera_lock_s=1, check_lock_s=0.01)
        second = Runner(engine, [TareaPeriodica("segundo", 0.01, second_task)], espera_lock_s=0.01, check_lock_s=0.01)
        running = [asyncio.create_task(first.ejecutar())]
        try:
            await wait_until(lambda: first.activo and bool(first_calls))
            running.append(asyncio.create_task(second.ejecutar()))
            def terminate_test_leader():
                with engine.begin() as db:
                    pid = db.scalar(text("SELECT pid FROM pg_locks WHERE locktype='advisory' AND objid=:id AND granted"), {"id": LOCK_ID})
                    assert pid
                    assert db.scalar(text("SELECT pg_terminate_backend(:pid)"), {"pid": pid})
            await asyncio.to_thread(terminate_test_leader)
            await wait_until(lambda: second.activo and bool(second_calls))
            assert not first.activo
            count = len(first_calls)
            await asyncio.sleep(0.05)
            assert len(first_calls) == count
        finally:
            for task in running:
                task.cancel()
            await asyncio.gather(*running, return_exceptions=True)
    asyncio.run(scenario())


def test_failed_task_reports_no_success_and_does_not_stop_other_tasks(engine):
    async def failing():
        raise RuntimeError("dato privado")

    async def successful():
        pass

    async def scenario():
        runner = Runner(engine, (t for t in [TareaPeriodica("falla", 0.01, failing), TareaPeriodica("ok", 0.01, successful)]))
        task = asyncio.create_task(runner.ejecutar())
        try:
            for _ in range(100):
                state = runner.estado()["tareas"]
                if state["ok"]["ultimo_exito"] and state["falla"]["error"]:
                    assert state["falla"]["ultimo_exito"] is None
                    assert state["falla"]["error"] == "RuntimeError"
                    return
                await asyncio.sleep(0.01)
            raise AssertionError("No se ejecutaron las tareas")
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
    asyncio.run(scenario())


def test_shutdown_waits_for_pending_lock_acquisition_and_releases_it(engine):
    import threading
    started, release = threading.Event(), threading.Event()

    class SlowRunner(Runner):
        def _tomar_lock(self):
            started.set()
            assert release.wait(2)
            return super()._tomar_lock()

    async def scenario():
        runner = SlowRunner(engine, [])
        task = asyncio.create_task(runner.ejecutar())
        try:
            assert await asyncio.to_thread(started.wait, 2)
            task.cancel()
            await asyncio.sleep(0.02)
            release.set()
            await asyncio.gather(task, return_exceptions=True)
            replacement = Runner(engine, [])
            try:
                assert await asyncio.to_thread(replacement._tomar_lock)
                assert not runner.activo
            finally:
                await asyncio.to_thread(replacement._soltar_lock)
        finally:
            release.set()
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
    asyncio.run(scenario())
