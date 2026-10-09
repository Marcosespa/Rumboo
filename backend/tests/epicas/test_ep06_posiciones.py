"""EP-06 · Posiciones e historial: sin datos inventados y lo antiguo no reemplaza lo reciente."""
from datetime import UTC, datetime, timedelta
from tests.ayudas import send_callback, trip_body
from tests.satelital.test_flujo_satrack import connect_account


def _positions_job(client, headers, satrack):
    _, fleet = connect_account(client, headers, satrack)
    trip = client.post("/api/viajes", json=trip_body(departure_in_h=0.5), headers=headers).json()
    send_callback(client, fleet["job_id"], "vehicles", vehicles=[{"plate": "ABC123"}])
    client.post(f"/api/viajes/{trip['id']}/transiciones", json={"estado": "en_ruta"}, headers=headers)
    client.post("/api/cuenta-satelital/consultar", headers=headers)
    return trip, satrack.jobs[-1]


def test_older_report_does_not_replace_latest_location(client, login, satrack):
    headers = login()
    _, job = _positions_job(client, headers, satrack)
    recent = datetime.now(UTC)
    send_callback(client, job["job_id"], "positions", positions=[{"plate": "ABC123", "lat": 5.0, "lng": -74.0, "reported_at": recent.isoformat()}])
    client.post("/api/cuenta-satelital/consultar", headers=headers)
    older = {"plate": "ABC123", "lat": 4.0, "lng": -73.0, "reported_at": (recent - timedelta(hours=1)).isoformat()}
    assert send_callback(client, satrack.jobs[-1]["job_id"], "positions", positions=[older]).status_code == 200
    assert client.get("/api/vehiculos", headers=headers).json()["items"][0]["ultima_posicion"]["lat"] == 5.0


def test_missing_coordinates_stay_empty(client, login, satrack):
    headers = login()
    trip, job = _positions_job(client, headers, satrack)
    send_callback(client, job["job_id"], "positions", positions=[{"plate": "ABC123", "address": "Sin señal"}])
    history = client.get(f"/api/viajes/{trip['id']}/posiciones", headers=headers).json()
    assert history and history[-1]["lat"] is None and history[-1]["lng"] is None
    assert history[-1]["velocidad_kmh"] is None and history[-1]["reportado_en"] is None
