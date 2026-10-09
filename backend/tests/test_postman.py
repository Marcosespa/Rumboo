import json
import re
from starlette.routing import Match
from tests.conftest import BACKEND

COLECCION = BACKEND.parent / "postman" / "rumboo.postman_collection.json"


def requests(items):
    for item in items:
        yield from requests(item["item"]) if "item" in item else [item["request"]]


def test_postman_collection_only_uses_existing_backend_routes(app):
    faltantes = []
    for request in requests(json.loads(COLECCION.read_text())["item"]):
        url = request["url"] if isinstance(request["url"], str) else request["url"]["raw"]
        if not url.startswith("{{baseUrl}}"):
            continue
        path = re.sub(r"\{\{\w+\}\}", "1", url.removeprefix("{{baseUrl}}").split("?")[0])
        scope = {"type": "http", "path": path, "method": request["method"]}
        if not any(route.matches(scope)[0] == Match.FULL for route in app.routes):
            faltantes.append(f"{request['method']} {path}")
    assert faltantes == []


def test_postman_environment_targets_the_disposable_stack():
    # Apuntar al stack normal con el usuario admin sobrescribiría las credenciales reales de Satrack.
    entorno = json.loads((COLECCION.parent / "rumboo-docker.postman_environment.json").read_text())
    valores = {v["key"]: v["value"] for v in entorno["values"]}
    assert valores["baseUrl"].endswith(":28000") and valores["satrackUrl"].endswith(":28081")
    assert valores["usuario"] == "postman" and valores["password"] == "" and valores["apiKey"] == ""
