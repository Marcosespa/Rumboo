import base64
import hashlib
import secrets
from datetime import timedelta
import bcrypt
from cryptography.fernet import Fernet
from app.db import now
from app.models import Sesion


def hash_password(password):
    if not 8 <= len(password.encode()) <= 72:
        raise ValueError("La contraseña debe tener entre 8 y 72 bytes")
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password, password_hash):
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except (ValueError, TypeError):
        return False


def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


def create_session(db, user, days):
    token = secrets.token_urlsafe(32)
    db.add(Sesion(token_hash=token_hash(token), usuario_id=user.id, expira_en=now() + timedelta(days=days)))
    db.commit()
    return token


def cipher(settings):
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(settings.secret_key.encode()).digest()))
