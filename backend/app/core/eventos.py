"""Eventos persistidos con el cambio de negocio, consumidores por aplicación.

Los consumidores son funciones de BD: cambios y confirmación se guardan juntos.
HTTP se ejecuta después desde sus consultas persistidas. Errores sin secretos.
"""
import asyncio
import logging
from datetime import timedelta
from uuid import uuid4
from sqlalchemy import func, or_, select
from app.core.db import now
from app.core.models import EntregaPendiente

logger = logging.getLogger(__name__)


def publicar(db, nombre, *, clave=None, **datos):
    bus = db.info.get("eventos")
    if bus is None:
        raise RuntimeError("La sesión debe usar el bus de su aplicación")
    key = clave or f"{nombre}:{datos.get('viaje_id', uuid4())}"
    for destinatario in bus.destinatarios(nombre):
        db.add(EntregaPendiente(transportadora_id=datos["transportadora_id"], evento=nombre,
                                destinatario=destinatario, clave=key, datos=datos))


class Bus:
    def __init__(self, sessions=None, max_intentos=5, lease_s=60):
        self.sessions = sessions
        self.max_intentos = max_intentos
        self.lease_s = lease_s
        self._consumidores = {}
        self._eventos = {}

    def suscribir(self, nombre, funcion, *, destinatario):
        if destinatario in self._consumidores:
            raise ValueError("El consumidor ya está registrado")
        self._consumidores[destinatario] = funcion
        self._eventos.setdefault(nombre, []).append(destinatario)

    def destinatarios(self, nombre):
        return tuple(self._eventos.get(nombre, ()))

    def _reclamar(self):
        if not self._consumidores:
            return None
        at = now()
        with self.sessions() as db:
            row = db.scalar(select(EntregaPendiente).where(
                EntregaPendiente.destinatario.in_(tuple(self._consumidores)),
                or_((EntregaPendiente.estado == "pendiente") & (EntregaPendiente.proximo_intento <= at),
                    (EntregaPendiente.estado == "ejecutando") & (EntregaPendiente.reclamada_hasta <= at))
            ).order_by(EntregaPendiente.creado_en, EntregaPendiente.id).with_for_update(skip_locked=True).limit(1))
            if row is None:
                return None
            row.estado = "ejecutando"
            row.intentos += 1
            row.reclamacion = str(uuid4())
            row.reclamada_hasta = at + timedelta(seconds=self.lease_s)
            claim = (row.id, row.reclamacion)
            db.commit()
            return claim

    def _aplicar(self, claim):
        with self.sessions() as db:
            row = db.scalar(select(EntregaPendiente).where(EntregaPendiente.id == claim[0],
                EntregaPendiente.reclamacion == claim[1], EntregaPendiente.estado == "ejecutando").with_for_update())
            if row is None:
                return
            self._consumidores[row.destinatario](db, **row.datos)
            row.estado = "entregado"
            row.terminado_en = now()
            row.reclamacion = None
            row.reclamada_hasta = None
            row.error_codigo = None
            db.commit()

    def _fallo(self, claim, error_code):
        with self.sessions() as db:
            row = db.scalar(select(EntregaPendiente).where(EntregaPendiente.id == claim[0],
                EntregaPendiente.reclamacion == claim[1]).with_for_update())
            if row is None or row.estado != "ejecutando":
                return
            row.estado = "fallido" if row.intentos >= self.max_intentos else "pendiente"
            row.error_codigo = error_code[:100]
            row.proximo_intento = now() + timedelta(seconds=(2, 10, 30)[min(row.intentos - 1, 2)])
            row.reclamacion = None
            row.reclamada_hasta = None
            db.commit()

    async def despachar(self, limit=20):
        for _ in range(limit):
            claim = await asyncio.to_thread(self._reclamar)
            if claim is None:
                break
            try:
                await asyncio.to_thread(self._aplicar, claim)
            except Exception as exc:
                await asyncio.to_thread(self._fallo, claim, type(exc).__name__)
                logger.warning("Entrega pendiente falló; se conserva para recuperación id=%s", claim[0])

    def estado(self):
        with self.sessions() as db:
            return dict(db.execute(select(EntregaPendiente.estado, func.count())
                                   .group_by(EntregaPendiente.estado)).all())
