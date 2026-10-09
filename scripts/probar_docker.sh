#!/usr/bin/env bash
# Despliega un stack aislado (proyecto rumboo-prueba, simulador, puertos 28000/28081) y ejecuta la colección Postman.
# No usa el .env real: genera .env.prueba (ignorado por git) la primera vez. Uso: scripts/probar_docker.sh [--down]
set -euo pipefail
cd "$(dirname "$0")/.."
ENV_FILE=.env.prueba
COMPOSE=(docker compose -p rumboo-prueba --env-file "$ENV_FILE")

if [ "${1:-}" = "--down" ]; then "${COMPOSE[@]}" down -v; rm -f "$ENV_FILE"; exit 0; fi

if [ ! -f "$ENV_FILE" ]; then
    umask 077
    python3 - > "$ENV_FILE" <<'EOF'
import base64, secrets
print(f"""POSTGRES_PASSWORD={secrets.token_hex(24)}
SECRET_KEY={secrets.token_hex(32)}
ENCRYPTION_KEYS={base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()}
SATRACK_SERVICE_API_KEY={secrets.token_hex(32)}
CALLBACK_SECRET={secrets.token_hex(32)}
PROVIDER=simulator
SEED_DEMO=false
BOOTSTRAP_USERNAME=postman
BOOTSTRAP_PASSWORD={secrets.token_urlsafe(18)}
BOOTSTRAP_CARRIER=Transportes Postman
API_PORT=28000
SCRAPER_PORT=28081""")
EOF
fi
valor() { grep "^$1=" "$ENV_FILE" | cut -d= -f2-; }

"${COMPOSE[@]}" up -d --build --wait
npx -y newman@6.2.2 run postman/rumboo.postman_collection.json -e postman/rumboo-docker.postman_environment.json \
    --env-var baseUrl=http://localhost:28000 --env-var satrackUrl=http://localhost:28081 \
    --env-var usuario=postman --env-var "password=$(valor BOOTSTRAP_PASSWORD)" \
    --env-var "apiKey=$(valor SATRACK_SERVICE_API_KEY)" --bail
echo "Stack en http://localhost:28000/docs · detener y borrar: scripts/probar_docker.sh --down"
