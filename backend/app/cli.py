import argparse
import getpass
import os
from datetime import timedelta
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from app import modelos  # noqa: F401  (registra todas las tablas)
from app.acceso.servicio import create_user
from app.auditoria.models import Evento
from app.core.config import Settings
from app.core.db import make_engine, now
from app.core.seguridad import cipher
from app.operacion.models import Conductor, Remesa, Vehiculo, Viaje
from app.satelital.models import ConsultaSatelital, CuentaSatelital, Posicion


def seed_demo(db, settings, user):
    tenant = user.transportadora_id
    if db.scalar(select(Viaje.id).where(Viaje.transportadora_id == tenant)):
        return
    account = db.scalar(select(CuentaSatelital).where(CuentaSatelital.transportadora_id == tenant))
    if not account:
        account = CuentaSatelital(transportadora_id=tenant, usuario="demo", password_cifrado=cipher(settings).encrypt(b"demo").decode(), estado="ok", ultima_consulta_ok=now())
        db.add(account)
        db.flush()
    query = ConsultaSatelital(job_id=str(uuid4()), transportadora_id=tenant, cuenta_satelital_id=account.id, cuenta_version=1,
                             tipo="positions", placas=["ABC123", "XYZ789", "DEF456"], estado="ok", respondido_en=now())
    db.add(query)
    db.flush()
    samples = [("ABC123", "Juan Pérez", "en_ruta", "Cali", 4.49, -74.2),
               ("XYZ789", "María Torres", "programado", "Medellín", 4.65, -74.08),
               ("DEF456", "Carlos Rojas", "entregado", "Girardot", 4.3, -74.8)]
    for i, (plate, name, state, destination, lat, lng) in enumerate(samples):
        driver = Conductor(transportadora_id=tenant, nombre=name, cedula=str(1012345600 + i), telefono=f"+57300123456{i}", autoriza_contacto=True, autorizado_en=now())
        vehicle = Vehiculo(transportadora_id=tenant, placa=plate, propietario="Flota demo", en_satelital=True)
        db.add_all([driver, vehicle])
        db.flush()
        trip = Viaje(transportadora_id=tenant, manifiesto=f"DEMO-{1001 + i}", conductor_id=driver.id, vehiculo_id=vehicle.id, origen="Bogotá", destino=destination,
                     salida_estimada=now() - timedelta(hours=2) if state != "programado" else now() + timedelta(minutes=30),
                     llegada_estimada=now() + timedelta(hours=8), peso_salida_kg=12000 + i * 1000, estado=state)
        db.add(trip)
        db.flush()
        db.add(Remesa(transportadora_id=tenant, viaje_id=trip.id, numero=f"R-{1001+i}", cliente="Cliente de demostración", peso_kg=trip.peso_salida_kg, cantidad=250))
        position = Posicion(transportadora_id=tenant, vehiculo_id=vehicle.id, viaje_id=trip.id, consulta_id=query.job_id,
                            lat=lat, lng=lng, velocidad_kmh=45 if state == "en_ruta" else 0, direccion="Ubicación de demostración · Colombia",
                            estado_gps="simulación", reportado_en=now(), capturado_en=now())
        db.add(position)
        db.flush()
        vehicle.ultima_posicion_id = position.id
        db.add(Evento(transportadora_id=tenant, viaje_id=trip.id, usuario_id=user.id, tipo="viaje_creado", detalle={"estado": state, "demo": True}))
    db.commit()


def main():
    parser = argparse.ArgumentParser(description="Usuarios y demo Rumboo")
    parser.add_argument("command", choices=["bootstrap", "crear-usuario", "seed-demo"])
    parser.add_argument("--transportadora", default="Transportes Demo")
    parser.add_argument("--usuario", default=None)
    args = parser.parse_args()
    settings = Settings()
    engine = make_engine(settings.database_url)
    with sessionmaker(engine, expire_on_commit=False)() as db:
        username = args.usuario or os.environ.get("BOOTSTRAP_USERNAME", "admin")
        password = os.environ.get("BOOTSTRAP_PASSWORD", "")
        if args.command == "bootstrap" and not password:
            print("Bootstrap omitido: crea el primer usuario con la CLI o configura BOOTSTRAP_PASSWORD")
            return
        if args.command == "crear-usuario":
            password = getpass.getpass("Contraseña: ")
        if not password:
            password = getpass.getpass("Contraseña del usuario inicial: ")
        user = create_user(db, os.environ.get("BOOTSTRAP_CARRIER", args.transportadora) if args.command == "bootstrap" else args.transportadora, username, password)
        if args.command == "seed-demo" or (args.command == "bootstrap" and os.environ.get("SEED_DEMO", "false").lower() == "true"):
            if os.environ.get("PROVIDER", "satrack") != "simulator":
                raise ValueError("La demo solo se puede crear con PROVIDER=simulator")
            seed_demo(db, settings, user)
        print("Usuario inicial disponible; las credenciales no se imprimen")
    engine.dispose()


if __name__ == "__main__":
    main()
