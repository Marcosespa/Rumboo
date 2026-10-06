import multiprocessing as mp
import os
import signal
import threading
import time
from pathlib import Path
from app.errors import ProviderError
from app.schemas import Position, Vehicle


def worker(connection, settings):
    if hasattr(os, "setsid"):
        os.setsid()
    from app.crawler import CrawlerSession
    crawler = CrawlerSession(settings)
    try:
        while True:
            request = connection.recv()
            if request is None:
                break
            try:
                rows = crawler.read(request["username"], request["password"])
                connection.send({"rows": rows})
            except ProviderError as exc:
                connection.send({"error": {"code": exc.code, "message": exc.message}})
            except Exception:
                connection.send({"error": {"code": "PROVIDER_UNAVAILABLE", "message": "No fue posible consultar Satrack"}})
    except (EOFError, BrokenPipeError):
        pass
    finally:
        crawler.close()
        connection.close()


class SatrackProvider:
    name = "satrack"

    def __init__(self, settings):
        self.settings = settings
        self.sessions = {}
        self.lock = threading.RLock()
        self.context = mp.get_context("spawn")

    def stop(self, session):
        process, connection = session["process"], session["connection"]
        try:
            if process.is_alive():
                if hasattr(os, "getpgid") and os.getpgid(process.pid) == process.pid:
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.terminate()
            process.join(timeout=2)
        except (ProcessLookupError, OSError):
            pass
        finally:
            connection.close()

    def cleanup(self):
        with self.lock:
            for key, session in list(self.sessions.items()):
                if not session["busy"] and time.monotonic() - session["used"] > self.settings.session_idle_s:
                    self.stop(self.sessions.pop(key))
        directory = Path(self.settings.data_dir) / "failures"
        if directory.exists():
            for path in directory.iterdir():
                if path.is_file() and path.stat().st_mtime < time.time() - 7 * 86400:
                    path.unlink(missing_ok=True)

    def acquire(self, account_id):
        with self.lock:
            session = self.sessions.get(account_id)
            if session and not session["process"].is_alive():
                self.stop(self.sessions.pop(account_id))
                session = None
            if not session:
                while len(self.sessions) >= self.settings.max_sessions:
                    idle = [(k, s) for k, s in self.sessions.items() if not s["busy"]]
                    if not idle:
                        raise ProviderError("PROVIDER_UNAVAILABLE", "Todas las sesiones satelitales están ocupadas")
                    key, _ = min(idle, key=lambda pair: pair[1]["used"])
                    self.stop(self.sessions.pop(key))
                parent, child = self.context.Pipe()
                process = self.context.Process(target=worker, args=(child, self.settings.model_dump()))
                process.start()
                child.close()
                session = {"process": process, "connection": parent, "used": time.monotonic(), "busy": False}
                self.sessions[account_id] = session
            session["busy"] = True
            return session

    def rows(self, account):
        session = self.acquire(account.id)
        try:
            pipe = session["connection"]
            pipe.send({"username": account.username, "password": account.password.get_secret_value()})
            if not pipe.poll(self.settings.job_timeout_s):
                self.cancel(account.id)
                raise ProviderError("TIMEOUT", "La consulta excedió el tiempo permitido")
            result = pipe.recv()
            if "error" in result:
                raise ProviderError(**result["error"])
            return result["rows"]
        except (OSError, EOFError):
            self.cancel(account.id)
            raise ProviderError("PROVIDER_UNAVAILABLE", "La sesión satelital se interrumpió")
        finally:
            with self.lock:
                session["busy"] = False
                session["used"] = time.monotonic()

    def fetch_positions(self, account):
        return [Position(**row) for row in self.rows(account)]

    def list_vehicles(self, account):
        return [Vehicle(**row) for row in self.rows(account)]

    def cancel(self, account_id):
        with self.lock:
            session = self.sessions.pop(account_id, None)
            if session:
                self.stop(session)

    def close(self):
        with self.lock:
            for session in self.sessions.values():
                self.stop(session)
            self.sessions.clear()

    @property
    def session_count(self):
        with self.lock:
            return len(self.sessions)
