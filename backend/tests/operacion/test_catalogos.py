from tests.ayudas import trip_body


def create_trips(client, headers):
    for i, (plate, cedula) in enumerate((("XYZ789", "1000000003"), ("ABC123", "1000000001"), ("DEF456", "1000000002"))):
        # Mismo nombre de conductor en los tres: el orden debe desempatar por id.
        response = client.post("/api/viajes", json=trip_body(manifiesto=f"MAN-{i}", placa=plate, cedula=cedula), headers=headers)
        assert response.status_code == 201


def test_vehicle_and_driver_catalogs_are_paginated_in_stable_order(client, login):
    headers = login()
    create_trips(client, headers)
    first = client.get("/api/vehiculos", params={"page": 1, "page_size": 2}, headers=headers).json()
    second = client.get("/api/vehiculos", params={"page": 2, "page_size": 2}, headers=headers).json()
    assert first["total"] == 3 and first["page"] == 1 and first["page_size"] == 2
    assert [v["placa"] for v in first["items"] + second["items"]] == ["ABC123", "DEF456", "XYZ789"]
    assert all("en_satelital" in v and "ultima_posicion" in v for v in second["items"])
    drivers = [client.get("/api/conductores", params={"page": p, "page_size": 2}, headers=headers).json() for p in (1, 2)]
    assert drivers[0]["total"] == 3
    assert [d["cedula"] for d in drivers[0]["items"] + drivers[1]["items"]] == ["1000000003", "1000000001", "1000000002"]


def test_catalogs_are_isolated_and_bounded(client, login):
    create_trips(client, login())
    other = login("Otra Empresa", "otro")
    for path in ("/api/vehiculos", "/api/conductores"):
        page = client.get(path, headers=other).json()
        assert page["items"] == [] and page["total"] == 0
        assert client.get(path, params={"page_size": 101}, headers=other).status_code == 422
        assert client.get(path).status_code == 401
