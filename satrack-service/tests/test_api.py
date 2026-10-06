from tests.conftest import job_body, wait_done


async def test_health_no_requiere_api_key(client_factory):
    client = await client_factory()
    response = await client.get("/health", headers={"X-Api-Key": ""})
    assert response.status_code == 200
    assert response.json()["provider"] == "simulator"


async def test_api_key_invalida_responde_401_antes_de_validar_el_body(client_factory):
    client = await client_factory()
    response = await client.post("/v1/jobs", json={"basura": True}, headers={"X-Api-Key": "otra"})
    assert response.status_code == 401
    response = await client.get(f"/v1/jobs/{job_body()['job_id']}", headers={"X-Api-Key": "otra"})
    assert response.status_code == 401


async def test_422_nunca_devuelve_la_contrasena(client_factory):
    client = await client_factory()
    response = await client.post("/v1/jobs", json=job_body(plates=(), password="SuperSecreta*99"))
    assert response.status_code == 422
    assert "SuperSecreta" not in response.text
    assert response.json()["errores"]


async def test_job_duplicado_responde_409(client_factory):
    client = await client_factory()
    body = job_body()
    assert (await client.post("/v1/jobs", json=body)).status_code == 202
    assert (await client.post("/v1/jobs", json=body)).status_code == 409


async def test_job_desconocido_responde_404(client_factory):
    client = await client_factory()
    response = await client.get("/v1/jobs/7f1c2e9a-5b1d-4c1e-9a43-0f3f8c1f2a10")
    assert response.status_code == 404


async def test_vehicles_devuelve_la_flota(client_factory):
    client = await client_factory()
    body = job_body(type_="vehicles", plates=())
    assert (await client.post("/v1/jobs", json=body)).status_code == 202
    status = await wait_done(client, body["job_id"])
    assert status["callback"] == "disabled"
    assert status["result"]["status"] == "ok"
    assert {v["plate"] for v in status["result"]["vehicles"]} >= {"ABC123", "XYZ789"}


async def test_positions_filtra_placas_y_reporta_las_que_no_estan(client_factory):
    client = await client_factory()
    body = job_body(plates=("ABC123", "zzz-999"))
    await client.post("/v1/jobs", json=body)
    result = (await wait_done(client, body["job_id"]))["result"]
    assert result["status"] == "partial"
    assert [p["plate"] for p in result["positions"]] == ["ABC123"]
    assert result["errors"] == [{"code": "VEHICLE_NOT_FOUND", "message": "La placa no está en la cuenta", "plate": "ZZZ999"}]


async def test_credenciales_invalidas_producen_auth_failed(client_factory):
    client = await client_factory()
    body = job_body(password="invalida")
    await client.post("/v1/jobs", json=body)
    result = (await wait_done(client, body["job_id"]))["result"]
    assert result["status"] == "failed"
    assert result["errors"][0]["code"] == "AUTH_FAILED"
    assert "invalida" not in str(result)
