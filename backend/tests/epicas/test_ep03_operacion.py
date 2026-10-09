"""EP-03 · Registro de la operación: catálogos reutilizados y validaciones del viaje."""
from tests.ayudas import trip_body


def test_driver_and_vehicle_catalogs_are_reused(client, login):
    headers = login()
    first = client.post("/api/viajes", json=trip_body(), headers=headers).json()
    client.post(f"/api/viajes/{first['id']}/transiciones", json={"estado": "cancelado", "motivo": "Prueba"}, headers=headers)
    second = client.post("/api/viajes", json=trip_body(manifiesto="MAN-2"), headers=headers)
    assert second.status_code == 201
    assert second.json()["conductor"]["id"] == first["conductor"]["id"]
    assert second.json()["vehiculo"]["id"] == first["vehiculo"]["id"]
    assert len(client.get("/api/conductores", headers=headers).json()["items"]) == 1
    assert len(client.get("/api/vehiculos", headers=headers).json()["items"]) == 1


def test_invalid_trips_are_rejected_with_field_errors(client, login):
    headers = login()
    same_city = trip_body() | {"destino": "bogotá", "origen": "Bogotá"}
    naive_date = trip_body() | {"salida_estimada": "2026-10-08T10:00:00"}
    repeated = trip_body()
    repeated["remesas"] = [repeated["remesas"][0]] * 2
    for body in (same_city, naive_date, repeated):
        response = client.post("/api/viajes", json=body, headers=headers)
        assert response.status_code == 422
        assert response.json()["detail"] == "Revisa los campos del formulario"
    assert client.get("/api/viajes", headers=headers).json()["total"] == 0
