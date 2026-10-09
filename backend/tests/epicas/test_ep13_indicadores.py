"""EP-13 · Indicadores: el panel refleja las transiciones de la operación."""
from tests.ayudas import trip_body


def test_panel_counts_follow_trip_states(client, login):
    headers = login()
    first = client.post("/api/viajes", json=trip_body(), headers=headers).json()
    client.post("/api/viajes", json=trip_body(manifiesto="MAN-2", placa="XYZ789", cedula="1099999999"), headers=headers)
    client.post(f"/api/viajes/{first['id']}/transiciones", json={"estado": "cancelado", "motivo": "Prueba"}, headers=headers)
    panel = client.get("/api/panel", headers=headers).json()
    assert panel["conteos"] == {"registrado": 1, "cancelado": 1}
    assert [t["manifiesto"] for t in panel["viajes_activos"]] == ["MAN-2"]
