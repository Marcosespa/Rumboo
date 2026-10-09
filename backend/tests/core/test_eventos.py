import asyncio
from datetime import timedelta
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from app.acceso.servicio import create_user
from app.auditoria.models import Evento
from app.auditoria.servicio import registrar_evento
from app.core import eventos
from app.core.db import now
from app.core.models import EntregaPendiente
from tests.ayudas import PASSWORD


def setup_bus(engine, consumers):
    bus = eventos.Bus()
    sessions = sessionmaker(engine, expire_on_commit=False, info={"eventos": bus})
    bus.sessions = sessions
    for name, function in consumers.items():
        bus.suscribir("prueba", function, destinatario=name)
    with sessions() as db:
        tenant = create_user(db, "Empresa", "operador", PASSWORD).transportadora_id
    return bus, sessions, tenant


def listener(db, *, transportadora_id, viaje_id):
    registrar_evento(db, transportadora_id, None, "recibido", {"origen": viaje_id})


def test_rollback_does_not_publish_and_restart_recovers_once(engine):
    bus, sessions, tenant = setup_bus(engine, {"auditar.v1": listener})
    with sessions() as db:
        eventos.publicar(db, "prueba", transportadora_id=tenant, viaje_id=7)
        db.rollback()
    assert bus.estado() == {}
    with sessions() as db:
        eventos.publicar(db, "prueba", transportadora_id=tenant, viaje_id=7)
        db.commit()
    # Nueva instancia sin memoria compartida: mismo nombre estable del consumidor.
    restarted = eventos.Bus(sessions)
    restarted.suscribir("prueba", listener, destinatario="auditar.v1")
    asyncio.run(restarted.despachar())
    asyncio.run(restarted.despachar())
    with sessions() as db:
        assert len(list(db.scalars(select(Evento)))) == 1
        assert db.scalar(select(EntregaPendiente.estado)) == "entregado"


def test_failure_rolls_back_effects_without_blocking_another_consumer(engine):
    def failing(db, **data):
        listener(db, **data)
        raise RuntimeError("texto que no se debe guardar")
    bus, sessions, tenant = setup_bus(engine, {"fallar.v1": failing, "auditar.v1": listener})
    with sessions() as db:
        eventos.publicar(db, "prueba", transportadora_id=tenant, viaje_id=7)
        db.commit()
    asyncio.run(bus.despachar())
    with sessions() as db:
        assert len(list(db.scalars(select(Evento)))) == 1
        failed = db.scalar(select(EntregaPendiente).where(EntregaPendiente.destinatario == "fallar.v1"))
        assert failed.estado == "pendiente" and failed.intentos == 1
        assert failed.error_codigo == "RuntimeError"
        failed.proximo_intento = now() - timedelta(seconds=1)
        db.commit()
    recovered = eventos.Bus(sessions)
    recovered.suscribir("prueba", listener, destinatario="fallar.v1")
    asyncio.run(recovered.despachar())
    with sessions() as db:
        assert len(list(db.scalars(select(Evento)))) == 2
    assert recovered.estado() == {"entregado": 2}


def test_expired_claim_is_recovered_and_previous_owner_cannot_apply(engine):
    bus, sessions, tenant = setup_bus(engine, {"auditar.v1": listener})
    with sessions() as db:
        eventos.publicar(db, "prueba", transportadora_id=tenant, viaje_id=7)
        db.commit()
    previous = bus._reclamar()
    assert bus._reclamar() is None
    with sessions() as db:
        row = db.get(EntregaPendiente, previous[0])
        row.reclamada_hasta = now() - timedelta(seconds=1)
        db.commit()
    replacement = bus._reclamar()
    assert replacement[0] == previous[0] and replacement[1] != previous[1]
    bus._aplicar(previous)
    bus._aplicar(replacement)
    with sessions() as db:
        assert len(list(db.scalars(select(Evento)))) == 1
        assert db.get(EntregaPendiente, previous[0]).intentos == 2


def test_abandoned_claims_stop_at_retry_limit(engine):
    bus, sessions, tenant = setup_bus(engine, {"auditar.v1": listener})
    bus.max_intentos = 1
    with sessions() as db:
        eventos.publicar(db, "prueba", transportadora_id=tenant, viaje_id=7)
        db.commit()
    old_claim = bus._reclamar()
    with sessions() as db:
        db.get(EntregaPendiente, old_claim[0]).reclamada_hasta = now() - timedelta(seconds=1)
        db.commit()
    assert bus._reclamar() is None
    bus._aplicar(old_claim)
    assert bus.estado() == {"fallido": 1}
    with sessions() as db:
        assert list(db.scalars(select(Evento))) == []


def test_exhausted_delivery_does_not_block_the_next_one(engine):
    bus, sessions, tenant = setup_bus(engine, {"auditar.v1": listener})
    with sessions() as db:
        eventos.publicar(db, "prueba", transportadora_id=tenant, viaje_id=1)
        db.commit()
        db.scalar(select(EntregaPendiente)).intentos = bus.max_intentos
        db.commit()
        eventos.publicar(db, "prueba", transportadora_id=tenant, viaje_id=2)
        db.commit()
    asyncio.run(bus.despachar())
    assert bus.estado() == {"fallido": 1, "entregado": 1}
    with sessions() as db:
        assert [e.detalle["origen"] for e in db.scalars(select(Evento))] == [2]
