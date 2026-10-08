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
