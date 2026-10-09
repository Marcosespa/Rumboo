import secrets
from datetime import timedelta
from sqlalchemy import delete, select
from app.acceso.models import Sesion, Transportadora, Usuario
from app.acceso.schemas import ConfiguracionDTO, TransportadoraDTO, UsuarioDTO
from app.core.db import aware, now
from app.core.errores import NoAutorizado
from app.core.seguridad import hash_password, token_hash, verify_password

DUMMY_HASH = hash_password("invalid-login-placeholder")


def user_info(user):
    return user.model_dump()


def _user_dto(user):
    return UsuarioDTO(id=user.id, usuario=user.usuario, nombre=user.nombre, transportadora_id=user.transportadora_id,
                      transportadora=TransportadoraDTO(id=user.transportadora_id, nombre=user.transportadora.nombre))


def authenticate(db, username, password, session_days):
    user = db.scalar(select(Usuario).where(Usuario.usuario == username.strip()))
    valid = verify_password(password, user.password_hash if user else DUMMY_HASH)
    if not user or not user.activo or not valid:
        raise NoAutorizado("Usuario o contraseña incorrectos")
    db.execute(delete(Sesion).where(Sesion.expira_en < now()))
    return create_session(db, user, session_days), _user_dto(user)


def create_session(db, user, days):
    token = secrets.token_urlsafe(32)
    db.add(Sesion(token_hash=token_hash(token), usuario_id=user.id, expira_en=now() + timedelta(days=days)))
    db.commit()
    return token


def user_for_token(db, token):
    session = db.get(Sesion, token_hash(token))
    if session is None or aware(session.expira_en) <= now() or not session.usuario.activo:
        return None
    return _user_dto(session.usuario)


def revoke_session(db, token):
    db.execute(delete(Sesion).where(Sesion.token_hash == token_hash(token)))
    db.commit()


def create_user(db, name, username, password):
    existing = db.scalar(select(Usuario).where(Usuario.usuario == username))
    if existing:
        return _user_dto(existing)
    carrier = db.scalar(select(Transportadora).where(Transportadora.nombre == name))
    if not carrier:
        carrier = Transportadora(nombre=name)
        db.add(carrier)
        db.flush()
    user = Usuario(transportadora_id=carrier.id, usuario=username, nombre=username, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    return _user_dto(user)


def lock_carrier(db, tenant):
    """Serializa operaciones de una transportadora (p. ej. reservas de conductor y vehículo)."""
    db.scalar(select(Transportadora).where(Transportadora.id == tenant).with_for_update())


def query_frequency_min(db, tenant):
    return db.get(Transportadora, tenant).frecuencia_consulta_min


def configuracion(db, tenant):
    return ConfiguracionDTO(frecuencia_consulta_min=query_frequency_min(db, tenant))
