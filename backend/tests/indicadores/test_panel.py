from tests.ayudas import trip_body


def test_panel_summarizes_the_operation(client, login):
    headers = login()
    client.post("/api/viajes", json=trip_body(), headers=headers)
    panel = client.get("/api/panel", headers=headers).json()
    assert panel["conteos"] == {"registrado": 1}
    assert panel["entregados_hoy"] == 0
    assert panel["cuenta_satelital"] is None
    assert [t["manifiesto"] for t in panel["viajes_activos"]] == ["MAN-1"]
