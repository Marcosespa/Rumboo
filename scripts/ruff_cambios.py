"""Ruff solo sobre las líneas cambiadas respecto a una base: el código nuevo entra limpio sin exigir arreglar la deuda vecina.

Uso: python3 scripts/ruff_cambios.py [--base REF] [archivo.py ...]   (sin archivos: todos los .py cambiados)
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RUFF = ["uvx", "ruff@0.8.6"]


def git(*args):
    return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, check=False).stdout


def changed_lines(base, path):
    """Líneas del archivo actual añadidas o modificadas desde base; None si el archivo es nuevo (todas cuentan)."""
    if path in git("ls-files", "--others", "--exclude-standard", "--", path).split():
        return None
    lines = set()
    for start, count in re.findall(r"^@@ .* \+(\d+)(?:,(\d+))? @@", git("diff", "-U0", base, "--", path), re.M):
        lines.update(range(int(start), int(start) + int(count or 1)))
    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=None)
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()
    base = args.base or git("merge-base", "main", "HEAD").strip() or "HEAD"
    files = [str(Path(f).resolve().relative_to(RAIZ)) for f in args.files] or sorted(
        {*git("diff", "--name-only", "--diff-filter=ACMR", base).split(), *git("ls-files", "--others", "--exclude-standard").split()})
    files = [f for f in files if f.endswith(".py") and f.startswith(("backend/", "satrack-service/")) and (RAIZ / f).exists()]
    if not files:
        print("sin archivos Python cambiados")
        return 0
    report = subprocess.run([*RUFF, "check", "--output-format", "json", *files], cwd=RAIZ, capture_output=True, text=True, check=False)
    problems = []
    for item in json.loads(report.stdout or "[]"):
        path = str(Path(item["filename"]).resolve().relative_to(RAIZ))
        lines = changed_lines(base, path)
        if lines is None or item["location"]["row"] in lines:
            problems.append(f"{path}:{item['location']['row']}: {item['code']} {item['message']}")
    print("\n".join(problems) or f"ruff ok en {len(files)} archivo(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
