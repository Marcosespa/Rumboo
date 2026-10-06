"""Generate local demo configuration without disclosing secrets or replacing an existing file."""
import os
from pathlib import Path
import secrets

target = Path(__file__).resolve().parents[1] / ".env"
values = {"POSTGRES_PASSWORD": secrets.token_hex(24), "SECRET_KEY": secrets.token_hex(32),
          "SATRACK_SERVICE_API_KEY": secrets.token_hex(32), "CALLBACK_SECRET": secrets.token_hex(32),
          "BOOTSTRAP_PASSWORD": secrets.token_urlsafe(18)}
template = target.with_name(".env.example").read_text()
lines = [f"{line.split('=', 1)[0]}={values[line.split('=', 1)[0]]}" if "=" in line and line.split('=', 1)[0] in values else line for line in template.splitlines()]
try:
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
except FileExistsError:
    print(".env ya existe; se conserva su configuración")
else:
    with os.fdopen(descriptor, "w") as output:
        output.write("\n".join(lines) + "\n")
    print(".env creado para demo local. Consulta BOOTSTRAP_USERNAME y BOOTSTRAP_PASSWORD en ese archivo para entrar.")
