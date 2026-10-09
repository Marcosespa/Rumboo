"""EP-05 · Cuenta satelital y consultas: una consulta pendiente por cuenta y estado consultable."""
from tests.ayudas import send_callback
from tests.satelital.test_flujo_satrack import connect_account


def test_only_one_pending_query_per_account(client, login, satrack):
    headers = login()
    _, job = connect_account(client, headers, satrack)
    again = client.post("/api/cuenta-satelital/sincronizar", headers=headers)
    assert again.status_code == 202
    assert again.json()["status"] == "pendiente" and again.json()["job_id"] == job["job_id"]
    assert len(satrack.jobs) == 1


def test_query_status_is_readable_until_resolved(client, login, satrack):
    headers = login()
    _, job = connect_account(client, headers, satrack)
    url = f"/api/consultas-satelitales/{job['job_id']}"
    assert client.get(url, headers=headers).json()["estado"] == "pendiente"
    send_callback(client, job["job_id"], "vehicles", vehicles=[{"plate": "ABC123"}])
    assert client.get(url, headers=headers).json()["estado"] == "ok"
    assert client.get("/api/cuenta-satelital", headers=headers).json()["consulta_pendiente"] is False


def test_invalid_credentials_block_new_queries(client, login, satrack):
    headers = login()
    _, job = connect_account(client, headers, satrack)
    send_callback(client, job["job_id"], "vehicles", status="failed", errors=[{"code": "AUTH_FAILED", "message": "Clave"}])
    assert client.get("/api/cuenta-satelital", headers=headers).json()["estado"] == "credenciales_invalidas"
    assert client.post("/api/cuenta-satelital/sincronizar", headers=headers).status_code == 409


def test_queries_need_an_account_and_trips(client, login):
    headers = login()
    without_account = client.post("/api/cuenta-satelital/sincronizar", headers=headers)
    assert without_account.status_code == 409
    assert without_account.json()["detail"] == "Conecta tu cuenta de Satrack primero"
    assert client.post("/api/cuenta-satelital/consultar", headers=headers).status_code == 409
