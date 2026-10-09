from sqlalchemy import update
from app.acceso.models import Transportadora


def test_configuration_shows_each_carrier_its_own_parameters(app, client, login):
    first = login()
    second = login("Otra Empresa", "otro")
    with app.state.sessions() as db:
        db.execute(update(Transportadora).where(Transportadora.nombre == "Otra Empresa").values(frecuencia_consulta_min=10))
        db.commit()
    assert client.get("/api/configuracion", headers=first).json() == {"frecuencia_consulta_min": 5, "zona_horaria": "America/Bogota"}
    assert client.get("/api/configuracion", headers=second).json()["frecuencia_consulta_min"] == 10
    assert client.get("/api/configuracion").status_code == 401
