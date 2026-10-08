import asyncio
from types import SimpleNamespace
from app.core import eventos


def test_subscribers_run_after_dispatch_and_failures_are_isolated():
    db = SimpleNamespace(info={})
    received = []

    async def failing(**data):
        raise RuntimeError("falla")

    async def listener(**data):
        received.append(data)

    bus = eventos.Bus()
    bus.suscribir("viaje_registrado", failing)
    bus.suscribir("viaje_registrado", listener)
    eventos.publicar(db, "viaje_registrado", viaje_id=7)
    assert received == []
    asyncio.run(bus.despachar(db))
    assert received == [{"viaje_id": 7}]
    asyncio.run(bus.despachar(db))
    assert received == [{"viaje_id": 7}]
