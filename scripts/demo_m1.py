"""Resultado verificable de M1 (backend/PLAN.md §8.1) con procesos reales y desechables.

PostgreSQL en Docker, satrack-service sin modificar (simulador, CALLBACK_URL vacío) y la API detenida a mitad de un
job durante más que CONSULTA_TIMEOUT_S. Al volver, el runner debe recuperar el resultado sin ninguna petición HTTP y
el recorrido continúa: flota → viaje programado → ubicación → entregado. No lee ningún .env; genera secretos por
ejecución y borra todo al terminar.

Uso (desde backend/): uv run python ../scripts/demo_m1.py
"""
import base64
import os
import secrets
import socket
import subprocess
import sys
import tempfile
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
import httpx
import psycopg

RAIZ = Path(__file__).resolve().parents[1]
TIMEOUT_S = 10  # mismo camino de código que los 240 s de producción, sin esperar 4 minutos


def puerto_libre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def esperar(condicion, segundos, que):
    limite = time.monotonic() + segundos
    while time.monotonic() < limite:
        valor = condicion()
        if valor:
            return valor
        time.sleep(0.3)
    raise RuntimeError(f"No ocurrió a tiempo: {que}")


def responde(url):
    try:
        return httpx.get(url, timeout=2).status_code == 200
    except httpx.HTTPError:
        return False


class Demo:
    def __init__(self, tmp):
        self.tmp = Path(tmp)
        self.pg, self.api_port, self.sat_port = puerto_libre(), puerto_libre(), puerto_libre()
        self.contenedor = f"rumboo-demo-m1-{os.getpid()}"
        clave_pg = secrets.token_hex(16)
        self.usuario, self.clave = "demo", secrets.token_urlsafe(18)
        self.env = {**os.environ, "PYTHONUNBUFFERED": "1",
                    "DATABASE_URL": f"postgresql+psycopg://rumboo:{clave_pg}@127.0.0.1:{self.pg}/rumboo_demo",
                    "SECRET_KEY": secrets.token_hex(32),
                    "ENCRYPTION_KEYS": base64.urlsafe_b64encode(secrets.token_bytes(32)).decode(),
                    "SATRACK_SERVICE_API_KEY": secrets.token_hex(32), "CALLBACK_SECRET": secrets.token_hex(32),
                    "SATRACK_SERVICE_URL": f"http://127.0.0.1:{self.sat_port}", "PROVIDER": "simulator", "CALLBACK_URL": "",
                    "DATA_DIR": str(self.tmp / "satrack"), "CONSULTA_TIMEOUT_S": str(TIMEOUT_S),
                    "BOOTSTRAP_USERNAME": self.usuario, "BOOTSTRAP_PASSWORD": self.clave, "BOOTSTRAP_CARRIER": "Transportes Demo"}
        self.clave_pg = clave_pg
        self.procesos = {}
        self.api = f"http://127.0.0.1:{self.api_port}"
        self.token = None

    def paso(self, texto, ok=True):
        print(f"[{'OK' if ok else 'FALLA'}] {texto}", flush=True)
        if not ok:
            raise RuntimeError(texto)

    def correr(self, nombre, comando, cwd):
        log = open(self.tmp / f"{nombre}.log", "w")
        self.procesos[nombre] = subprocess.Popen(comando, cwd=cwd, env=self.env, stdout=log, stderr=subprocess.STDOUT)

    def detener(self, nombre):
        proceso = self.procesos.pop(nombre)
        proceso.terminate()
        proceso.wait(timeout=15)

    def arrancar_api(self, runner):
        self.env["SCHEDULER_ENABLED"] = "true" if runner else "false"
        # cwd temporal: pydantic-settings no encuentra ningún .env del repositorio.
        self.correr("api", ["uv", "run", "--quiet", "--project", str(RAIZ / "backend"), "uvicorn", "app.main:create_app",
                            "--factory", "--app-dir", str(RAIZ / "backend"), "--host", "127.0.0.1",
                            "--port", str(self.api_port)], self.tmp)
        esperar(lambda: responde(f"{self.api}/health"), 60, "arranque de la API")

    def db(self, sql, *args):
        with psycopg.connect(f"postgresql://rumboo:{self.clave_pg}@127.0.0.1:{self.pg}/rumboo_demo") as conn:
            return conn.execute(sql, args).fetchall()

    def http(self, metodo, ruta, **kwargs):
        return httpx.request(metodo, f"{self.api}{ruta}", headers={"Authorization": f"Bearer {self.token}"}, timeout=15, **kwargs)

    def preparar(self):
        subprocess.run(["docker", "run", "-d", "--name", self.contenedor, "-e", "POSTGRES_USER=rumboo",
                        "-e", f"POSTGRES_PASSWORD={self.clave_pg}", "-e", "POSTGRES_DB=rumboo_demo",
                        "-p", f"127.0.0.1:{self.pg}:5432", "postgres:16-alpine"], check=True, capture_output=True)
        esperar(lambda: self._pg_listo(), 60, "PostgreSQL")
        subprocess.run(["uv", "run", "--quiet", "alembic", "upgrade", "head"], cwd=RAIZ / "backend", env=self.env,
                       check=True, capture_output=True)
        subprocess.run(["uv", "run", "--quiet", "--project", str(RAIZ / "backend"), "python", "-m", "app.cli", "bootstrap"],
                       cwd=self.tmp, env=self.env | {"PYTHONPATH": str(RAIZ / "backend")}, check=True, capture_output=True)
        self.correr("satrack", ["uv", "run", "--quiet", "--project", str(RAIZ / "satrack-service"), "uvicorn",
                                "app.main:create_app", "--factory", "--app-dir", str(RAIZ / "satrack-service"),
                                "--host", "127.0.0.1", "--port", str(self.sat_port)], self.tmp)
        esperar(lambda: responde(f"http://127.0.0.1:{self.sat_port}/health"), 60, "arranque del scraper")
        self.paso("Entorno: PostgreSQL migrado, usuario creado por CLI y scraper simulador sin callback")

    def _pg_listo(self):
        try:
            self.db("SELECT 1")
            return True
        except psycopg.OperationalError:
            return False

    def ejecutar(self):
        self.preparar()
        self.arrancar_api(runner=False)
        r = httpx.post(f"{self.api}/api/auth/login", json={"usuario": self.usuario, "password": self.clave}, timeout=15)
        self.token = r.json()["token"]
        self.paso("Login", r.status_code == 200)
        r = self.http("PUT", "/api/cuenta-satelital", json={"usuario": "demo-satrack", "password": secrets.token_hex(8)})
        self.paso("Conectar Satrack: la consulta de flota queda registrada y enviada", r.status_code == 200)
        job, estado, intentos = self.db("SELECT job_id, estado, intentos FROM consultas_satelitales")[0]
        self.paso(f"PostgreSQL: consulta {job[:8]} {estado}, intentos={intentos}", estado == "pendiente" and intentos == 1)
        sat = httpx.get(f"http://127.0.0.1:{self.sat_port}/v1/jobs/{job}",
                        headers={"X-Api-Key": self.env["SATRACK_SERVICE_API_KEY"]}, timeout=10).json()
        self.paso("Scraper: job terminado y callback desactivado", sat["status"] == "done" and sat["callback"] == "disabled")
        self.detener("api")
        espera = TIMEOUT_S + 3
        print(f"     API detenida a mitad del job; se espera {espera} s (más que CONSULTA_TIMEOUT_S={TIMEOUT_S})", flush=True)
        time.sleep(espera)
        self.arrancar_api(runner=True)
        estado = esperar(lambda: (lambda e: e if e != "pendiente" else None)(
            self.db("SELECT estado FROM consultas_satelitales WHERE job_id=%s", job)[0][0]), 30, "reconciliación")
        fallos = self.db("SELECT fallos_consecutivos FROM cuentas_satelitales")[0][0]
        self.paso(f"Reinicio con runner: consulta {estado} sin ninguna petición de seguimiento (fallos={fallos})",
                  estado == "ok" and fallos == 0)
        flota = self.http("GET", "/api/vehiculos").json()
        self.paso(f"Flota completa: {flota['total']} vehículos con ubicación",
                  flota["total"] == 4 and all(v["en_satelital"] and v["ultima_posicion"] for v in flota["items"]))
        salida = datetime.now(UTC) + timedelta(minutes=30)
        viaje = self.http("POST", "/api/viajes", json={
            "manifiesto": "DEMO-M1-001", "origen": "Bogotá", "destino": "Girardot", "salida_estimada": salida.isoformat(),
            "llegada_estimada": (salida + timedelta(hours=5)).isoformat(),
            "conductor": {"nombre": "Juan Pérez", "cedula": "1012345678", "telefono": "3001234567", "autoriza_contacto": True},
            "vehiculo": {"placa": "ABC123", "propietario": "Flota demo"},
            "remesas": [{"numero": "R-1", "cliente": "Cliente", "peso_kg": 8000}]}).json()
        self.paso(f"Registrar viaje: estado {viaje['estado']}", viaje["estado"] == "programado")
        ruta = f"/api/viajes/{viaje['id']}/transiciones"
        self.paso("Iniciar ruta", self.http("POST", ruta, json={"estado": "en_ruta"}).json()["estado"] == "en_ruta")
        consulta = self.http("POST", "/api/cuenta-satelital/consultar").json()
        estado = esperar(lambda: (lambda e: e if e != "pendiente" else None)(
            self.http("GET", f"/api/consultas-satelitales/{consulta['job_id']}").json()["estado"]), 30, "ubicación")
        posiciones = self.http("GET", f"/api/viajes/{viaje['id']}/posiciones").json()
        self.paso(f"Ubicación por GET sin callback: consulta {estado}, {len(posiciones)} posición(es) en el viaje",
                  estado == "ok" and posiciones and posiciones[-1]["lat"] is not None)
        self.paso("Entregar", self.http("POST", ruta, json={"estado": "entregado"}).json()["estado"] == "entregado")

    def limpiar(self):
        for nombre in list(self.procesos):
            self.detener(nombre)
        subprocess.run(["docker", "rm", "-f", self.contenedor], capture_output=True)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="rumboo-demo-") as tmp:
        demo = Demo(tmp)
        try:
            demo.ejecutar()
            print("M1 verificado: recorrido completo con callback desactivado y recuperación tras reinicio.")
        except (RuntimeError, httpx.HTTPError, subprocess.CalledProcessError, KeyError) as err:
            print(f"Demo fallida: {err}", file=sys.stderr)
            for log in sorted(Path(tmp).glob("*.log")):
                print(f"--- {log.name}\n{log.read_text()[-2000:]}", file=sys.stderr)
            sys.exit(1)
        finally:
            demo.limpiar()
