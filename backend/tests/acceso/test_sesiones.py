from tests.ayudas import trip_body


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
    assert client.get("/api/vehiculos", headers=second).json() == []
