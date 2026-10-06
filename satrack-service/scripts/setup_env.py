"""Crea configuración privada para el microservicio independiente sin reemplazarla."""
import json
import os
import secrets
from pathlib import Path

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]


def create_private(path, content):
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        print("Se conserva", path.name)
        return
    with os.fdopen(fd, "w") as output:
        output.write(content)
    print("Creado", path.name)


def main():
    template = (ROOT / ".env.example").read_text()
    template = template.replace("replace-with-generated-secret", secrets.token_hex(32))
    create_private(ROOT / ".env", template)
    config = dotenv_values(ROOT / ".env")
    environment = json.loads((ROOT / "postman/satrack-local.postman_environment.json").read_text())
    environment["name"] = "Rumboo · Satrack (local privado)"
    for item in environment["values"]:
        if item["key"] == "apiKey":
            item["value"] = config["SATRACK_SERVICE_API_KEY"]
    create_private(ROOT / "postman/satrack-real.local.postman_environment.json",
                   json.dumps(environment, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
