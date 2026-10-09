"""EP-02 · Acceso y aislamiento: sesiones con vencimiento y ninguna escritura sobre otra transportadora."""
from datetime import UTC, datetime, timedelta
from sqlalchemy import update
from app.acceso.models import Sesion
from tests.ayudas import trip_body
from tests.satelital.test_flujo_satrack import connect_account


def test_requests_without_valid_token_are_rejected(client):
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/viajes", headers={"Authorization": "Bearer inventado"}).status_code == 401


def test_expired_session_is_rejected(app, client, login):
    headers = login()
    with app.state.sessions() as db:
        db.execute(update(Sesion).values(expira_en=datetime.now(UTC) - timedelta(seconds=1)))
        db.commit()
    assert client.get("/api/auth/me", headers=headers).status_code == 401


def test_other_carrier_cannot_modify_or_query_resources(client, login, satrack):
    first = login("Transportes Uno", "operador1")
    second = login("Transportes Dos", "operador2")
    trip = client.post("/api/viajes", json=trip_body(), headers=first).json()
    _, job = connect_account(client, first, satrack)

    transition = client.post(f"/api/viajes/{trip['id']}/transiciones", json={"estado": "cancelado", "motivo": "x"}, headers=second)
    assert transition.status_code == 404
    assert client.get(f"/api/consultas-satelitales/{job['job_id']}", headers=second).status_code == 404
    assert client.get("/api/cuenta-satelital", headers=second).json() is None
    assert client.get("/api/conductores", headers=second).json()["items"] == []
    assert client.get("/api/panel", headers=second).json()["conteos"] == {}
    assert client.get(f"/api/viajes/{trip['id']}", headers=first).json()["estado"] == "registrado"
