import base64
import hashlib
import bcrypt
from cryptography.fernet import Fernet


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


def cipher(settings):
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(settings.secret_key.encode()).digest()))
