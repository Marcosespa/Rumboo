#!/usr/bin/env bash
# Puerta de calidad: ruff (líneas cambiadas), fronteras, migraciones y pruebas. Uso: scripts/verificar.sh [base]
set -uo pipefail
cd "$(dirname "$0")/.."
fallos=(); no_verificado=()
paso() { printf '\n== %s\n' "$1"; }

paso "ruff"
python3 scripts/ruff_cambios.py ${1:+--base "$1"} || fallos+=("ruff")

paso "import-linter"
(cd backend && uv run --quiet lint-imports) || fallos+=("lint-imports")

paso "pytest backend"
if [ -n "${TEST_DATABASE_URL:-}" ] || (exec 3<>/dev/tcp/127.0.0.1/55432) 2>/dev/null; then
    (cd backend && uv run --quiet pytest -q) || fallos+=("pytest backend")
else
    echo "PostgreSQL de pruebas no disponible en 127.0.0.1:55432"; no_verificado+=("pytest backend")
fi

paso "pytest satrack-service"
(cd satrack-service && uv run --quiet pytest -q) || fallos+=("pytest satrack-service")

paso "resultado"
[ ${#no_verificado[@]} -gt 0 ] && echo "NO VERIFICADO: ${no_verificado[*]}"
[ ${#fallos[@]} -gt 0 ] && { echo "FALLA: ${fallos[*]}"; exit 1; }
[ ${#no_verificado[@]} -gt 0 ] && exit 2
echo "OK"
