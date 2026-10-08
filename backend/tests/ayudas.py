import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone

CALLBACK_SECRET = "test-callback-secret-0123"
PASSWORD = "clave-segura-123"


def trip_body(manifiesto="MAN-1", placa="ABC123", cedula="1012345678", departure_in_h=2.0):
    departure = datetime.now(timezone.utc) + timedelta(hours=departure_in_h)
    return {"manifiesto": manifiesto, "origen": "Bogotá", "destino": "Medellín",
            "salida_estimada": departure.isoformat(), "llegada_estimada": (departure + timedelta(hours=10)).isoformat(),
            "conductor": {"nombre": "Juan Pérez", "cedula": cedula, "telefono": "3001234567", "autoriza_contacto": True},
            "vehiculo": {"placa": placa, "propietario": "Flota"},
            "remesas": [{"numero": "R-1", "cliente": "Cliente", "peso_kg": 1000, "cantidad": 10},
                        {"numero": "R-2", "cliente": "Cliente", "peso_kg": 500}]}


def send_callback(client, job_id, kind, status="ok", vehicles=(), positions=(), errors=(), secret=CALLBACK_SECRET):
    payload = {"job_id": job_id, "type": kind, "status": status, "finished_at": datetime.now(timezone.utc).isoformat(),
               "vehicles": list(vehicles), "positions": list(positions), "errors": list(errors)}
    body = json.dumps(payload).encode()
    signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return client.post("/internal/satrack/callback", content=body,
                       headers={"X-Signature": signature, "X-Job-Id": job_id, "Content-Type": "application/json"})
