"""Prueba de lectura real con un environment Postman privado, sin imprimir secretos."""
import argparse
import json
import os
import time
from pathlib import Path
from uuid import uuid4

import httpx


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environment", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/live-result.json"))
    args = parser.parse_args()
    variables = {value["key"]: value["value"] for value in json.loads(args.environment.read_text())["values"]}
    with httpx.Client(base_url=variables["baseUrl"], headers={"X-Api-Key": variables["apiKey"]}, timeout=15) as client:
        health = client.get("/health")
        health.raise_for_status()
        print("Proveedor:", health.json()["provider"], flush=True)
        account = {"id": variables["accountId"], "username": variables["satrackUsername"], "password": variables["satrackPassword"]}
        results = []
        plates = []
        for kind in ("vehicles", "positions"):
            if kind == "positions" and not plates:
                break
            job_id = str(uuid4())
            response = client.post("/v1/jobs", json={"job_id": job_id, "type": kind, "account": account, "plates": plates})
            response.raise_for_status()
            print(kind, "aceptado:", response.status_code, flush=True)
            deadline = time.monotonic() + 150
            while time.monotonic() < deadline:
                response = client.get(f"/v1/jobs/{job_id}")
                response.raise_for_status()
                status = response.json()
                if status["status"] == "done":
                    result = status["result"]
                    print(kind, "resultado:", result["status"], "errores:", [error["code"] for error in result["errors"]], flush=True)
                    results.append(status)
                    if result["status"] == "failed":
                        raise RuntimeError("La consulta falló: " + ",".join(error["code"] for error in result["errors"]))
                    rows = result[kind]
                    print("Filas:", len(rows), "con coordenadas:", sum(row["lat"] is not None and row["lng"] is not None for row in rows), flush=True)
                    if kind == "vehicles":
                        plates = [row["plate"] for row in rows]
                    break
                time.sleep(2)
            else:
                raise RuntimeError("El job no terminó dentro del plazo")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as output:
        json.dump(results, output, indent=2, ensure_ascii=False)
    print("Resultado privado guardado en", args.output, flush=True)


if __name__ == "__main__":
    main()
