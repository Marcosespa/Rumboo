from datetime import datetime, timezone
import math
import time
from app.errors import ProviderError
from app.schemas import Account, Position, Vehicle


class SimulatorProvider:
    name = "simulator"
    plates = ("ABC123", "XYZ789", "DEF456", "GHI012")

    def check(self, account: Account):
        if account.password.get_secret_value() == "invalida":
            raise ProviderError("AUTH_FAILED", "Usuario o contraseña de Satrack incorrectos")
        if account.password.get_secret_value() == "captcha":
            raise ProviderError("CAPTCHA_REQUIRED", "Se requiere verificación manual en Satrack")

    def list_vehicles(self, account: Account):
        return [Vehicle(**(position.model_dump() | {"name": f"Camión {position.plate}"}))
                for position in self.fetch_positions(account)]

    def fetch_positions(self, account: Account):
        self.check(account)
        now = datetime.now(timezone.utc).replace(microsecond=0)
        phase = (time.time() % 3600) / 3600
        return [Position(plate=p, lat=4.65 - phase * .6 + i * .015,
                         lng=-74.08 - phase * .4 - i * .02,
                         speed_kmh=45 + 10 * math.sin(phase * math.pi), status="en movimiento",
                         address="Corredor Bogotá · Girardot (simulación)", reported_at=now,
                         reported_at_raw=now.isoformat()) for i, p in enumerate(self.plates)]

    def cancel(self, account_id):
        pass

    def close(self):
        pass

    @property
    def session_count(self):
        return 0
