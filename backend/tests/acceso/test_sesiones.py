from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from app.acceso.servicio import create_user
from app.main import create_app
from tests.ayudas import PASSWORD, trip_body
from tests.conftest import TEST_DATABASE_URL


def test_each_request_needs_a_single_db_connection(engine, settings, satrack):
    # Con una sola conexión en el pool, retener la de la autenticación bloquearía la segunda sesión del endpoint.
    small = create_engine(TEST_DATABASE_URL, pool_size=1, max_overflow=0, pool_timeout=2)
    app = create_app(settings, small, satrack)
    with TestClient(app) as client:
        with app.state.sessions() as db:
            create_user(db, "Transportes Uno", "operador1", PASSWORD)
        token = client.post("/api/auth/login", json={"usuario": "operador1", "password": PASSWORD}).json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        assert client.post("/api/viajes", json=trip_body(), headers=headers).status_code == 201
        assert client.put("/api/cuenta-satelital", json={"usuario": "u", "password": "p"}, headers=headers).status_code == 200
        assert client.post("/api/cuenta-satelital/sincronizar", headers=headers).status_code == 202


def test_login_me_and_logout(client, login):
    headers = login()
    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["transportadora"]["nombre"] == "Transportes Uno"
    assert client.post("/api/auth/logout", headers=headers).status_code == 200
    assert client.get("/api/auth/me", headers=headers).status_code == 401


def test_invalid_credentials_get_a_generic_error(client, login):
    login()
    response = client.post("/api/auth/login", json={"usuario": "operador1", "password": "incorrecta"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Usuario o contraseña incorrectos"}


def test_carriers_cannot_see_each_other(client, login):
    first = login("Transportes Uno", "operador1")
    second = login("Transportes Dos", "operador2")
    trip = client.post("/api/viajes", json=trip_body(), headers=first).json()
    assert client.get(f"/api/viajes/{trip['id']}", headers=second).status_code == 404
    assert client.get(f"/api/viajes/{trip['id']}/posiciones", headers=second).status_code == 404
    assert client.get("/api/viajes", headers=second).json()["total"] == 0
    assert client.get("/api/vehiculos", headers=second).json()["items"] == []
