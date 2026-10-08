import base64
import hashlib
import bcrypt
from cryptography.fernet import Fernet, MultiFernet


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
    """Cifra con la primera clave de ENCRYPTION_KEYS y descifra con cualquiera. La clave derivada de SECRET_KEY
    queda al final solo para leer datos anteriores; `python -m app.cli recifrar` los migra a la clave vigente."""
    legacy = Fernet(base64.urlsafe_b64encode(hashlib.sha256(settings.secret_key.encode()).digest()))
    return MultiFernet([*(Fernet(key) for key in settings.encryption_key_list), legacy])
