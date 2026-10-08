from sqlalchemy import select
from app.auditoria.models import Evento


def registrar_evento(db, tenant, trip_id, kind, detail, user_id=None):
    db.add(Evento(transportadora_id=tenant, viaje_id=trip_id, usuario_id=user_id, tipo=kind, detalle=detail))


def eventos_de_viaje(db, tenant, trip_id, limit=100):
    events = db.scalars(select(Evento).where(Evento.viaje_id == trip_id, Evento.transportadora_id == tenant).order_by(Evento.id.desc()).limit(limit))
    return [{"id": e.id, "tipo": e.tipo, "detalle": e.detalle, "creado_en": e.creado_en, "usuario_id": e.usuario_id} for e in events]
