from tests.ayudas import trip_body


def test_trip_without_satellite_account_stays_registered(client, login, satrack):
    response = client.post("/api/viajes", json=trip_body(), headers=login())
    assert response.status_code == 201
    trip = response.json()
    assert trip["estado"] == "registrado"
    assert trip["peso_salida_kg"] == 1500
    assert [e["tipo"] for e in trip["eventos"]] == ["viaje_creado"]
    assert satrack.jobs == []


def test_duplicate_manifest_and_busy_vehicle_are_conflicts(client, login):
    headers = login()
    assert client.post("/api/viajes", json=trip_body(), headers=headers).status_code == 201
    duplicate = client.post("/api/viajes", json=trip_body(cedula="1099999999", placa="XYZ789"), headers=headers)
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "Ya existe un viaje con ese manifiesto"
    busy = client.post("/api/viajes", json=trip_body(manifiesto="MAN-2", cedula="1099999999"), headers=headers)
    assert busy.status_code == 409
    assert busy.json()["detail"] == "El vehículo ya tiene un viaje activo"


def test_transitions_follow_the_state_machine(client, login):
    headers = login()
    trip = client.post("/api/viajes", json=trip_body(), headers=headers).json()
    url = f"/api/viajes/{trip['id']}/transiciones"
    assert client.post(url, json={"estado": "en_ruta"}, headers=headers).status_code == 409
    assert client.post(url, json={"estado": "cancelado"}, headers=headers).status_code == 422
    cancelled = client.post(url, json={"estado": "cancelado", "motivo": "Cliente canceló"}, headers=headers)
    assert cancelled.status_code == 200
    assert cancelled.json()["estado"] == "cancelado"
    assert client.post("/api/viajes", json=trip_body(manifiesto="MAN-2"), headers=headers).status_code == 201


def test_trip_listing_is_paginated(client, login):
    headers = login()
    client.post("/api/viajes", json=trip_body(), headers=headers)
    page = client.get("/api/viajes", params={"page": 1, "page_size": 5, "q": "abc"}, headers=headers).json()
    assert page["total"] == 1 and page["page"] == 1 and page["page_size"] == 5
    assert page["items"][0]["vehiculo"]["placa"] == "ABC123"
