# Microservicio Satrack

API FastAPI con Selenium/Chromium para consultar toda la flota y sus últimas posiciones. Funciona de forma independiente; opcionalmente entrega resultados al backend por callback HMAC. Reutiliza sesiones por cuenta y ejecuta Selenium en procesos cancelables.

## Arranque independiente

Desde esta carpeta:

```sh
uv sync --frozen
uv run python scripts/setup_env.py
docker compose up -d --build
```

El servicio escucha en `http://localhost:18081`; documentación interactiva en `/docs` y estado en `/health`. `SCRAPER_PORT` permite cambiar el puerto. La configuración privada `.env` se genera con una API key aleatoria; el script conserva archivos existentes. El Compose general del repositorio usa `localhost:8081` para su propio scraper.

Para ejecutar sin Docker, instala Chrome/Chromium y usa `uv run uvicorn app.main:create_app --factory --host 127.0.0.1 --port 18081 --workers 1`. Selenium Manager resuelve el driver. Las rutas `CHROME_BINARY` y `CHROMEDRIVER_PATH` permiten configurarlo explícitamente.

## Postman

1. Importa [la colección](postman/satrack-service.postman_collection.json) y el environment privado `postman/satrack-real.local.postman_environment.json` generado por el script.
2. Selecciona ese environment. Completa `satrackUsername` y `satrackPassword` como valores locales; `apiKey` y `baseUrl` ya están preparados.
3. Ejecuta la carpeta **Flujo completo** con el Collection Runner. Crea el job de vehículos, consulta su resultado y después pide las posiciones de las placas encontradas. El polling espera tres segundos entre consultas y se detiene tras 60 intentos o un error.
4. En **Visualize**, los resultados muestran la tabla de vehículos o posiciones: placa, alias, dirección, coordenadas, velocidad, estado y reporte. Si envías las peticiones manualmente con **Send**, cada envío hace una sola consulta: repite el mismo GET cada tres segundos hasta ver `status: done`. `queued` o `running` con `result: null` significa que el trabajo aún no ha terminado; Visualize indica que está en proceso. La dirección está en `result.vehicles[].address` para `vehicles` y en `result.positions[].address` para `positions`.

Si aparece **«Faltan variables»**, importa y selecciona el environment privado del paso 1, o completa los valores locales que indica el mensaje. Pegar el JSON del body no selecciona un environment. Con el body original `accountJson`, los scripts necesitan `satrackUsername` y `satrackPassword`; con un objeto `account` escrito directamente en el body, solo se necesitan las variables que ese body utilice. `apiKey` se resuelve desde las variables activas o un header explícito `X-Api-Key`. El id devuelto por el POST se guarda para consultar el resultado, incluso si el body usa `{{$guid}}`.

El environment compartible [satrack-local](postman/satrack-local.postman_environment.json) está vacío de credenciales. Los archivos `*.local.postman_environment.json`, `.env` y `data/` están excluidos de Git. El environment privado contiene secretos: úsalo localmente, sin compartirlo ni sincronizarlo en espacios compartidos.

## Contrato HTTP

`POST /v1/jobs` y `GET /v1/jobs/{job_id}` requieren `X-Api-Key`. Ejemplo del body (credenciales ilustrativas):

```json
{
  "job_id": "7f1c2e9a-5b1d-4c1e-9a43-0f3f8c1f2a10",
  "type": "vehicles",
  "account": {"id": "cuenta-1", "username": "usuario", "password": "clave"},
  "plates": []
}
```

La respuesta inicial es `202 {"job_id":"..."}`. El GET devuelve `queued`, `running` o `done`; al terminar, `result` contiene `status` (`ok`/`partial`/`failed`), `vehicles`, `positions`, `errors` y `finished_at`. Para `positions`, envía una o más placas colombianas (`ABC123`) en `plates`; se normalizan espacios y guiones y se informa `VEHICLE_NOT_FOUND` por placas ausentes.

Un job `vehicles` devuelve la flota con los datos disponibles de la ficha del mapa. Un job `positions` devuelve esos mismos datos para las placas solicitadas. La lista virtualizada se recorre para evitar devolver solo las filas visibles. Los campos que Satrack no expone quedan en `null`; `0,0` se considera ubicación ausente. La hora GPS se convierte de Colombia a UTC. El tooltip `Hoy/Ayer, hh:mm:ss` permite conservar una hora explícita; textos como `Hace 10 s` se conservan sin estimar una fecha. El identificador del DOM no se presenta como id de un dispositivo.

Los resultados viven en memoria una hora después de terminar. `MAX_RETAINED_JOBS=1000` limita esa retención, expulsando resultados terminados antiguos; sus UUID siguen deduplicados durante la hora. Un reinicio elimina jobs y sesiones. Respuestas: `401` API key inválida, `404` resultado ausente/vencido, `409` UUID repetido, `422` body inválido sin eco de credenciales, `503` cola/retención llena.

`CALLBACK_URL` vacío desactiva el callback. Para integrar con el backend configura una URL fija y `CALLBACK_SECRET` de al menos 16 caracteres. La entrega conserva cuatro intentos con pausas 2/10/30 segundos y headers `X-Job-Id`, `X-Timestamp` y `X-Signature: sha256=HMAC("{timestamp}.{body}")`; el backend rechaza firmas con más de 5 min; un fallo de entrega no elimina el resultado consultable. Usa una sola réplica/worker para preservar sesiones y consulta de resultados en memoria.

## Pruebas

```sh
uv run pytest -q
node --test tests/test_postman.cjs
uv run python scripts/check_live.py --environment postman/satrack-real.local.postman_environment.json
```

La primera orden usa simulación y pruebas de contrato, errores, firma, concurrencia, timeout, retención y extracción. La segunda comprueba los scripts Postman con body manual o variables y los mensajes por configuración faltante. La tercera realiza solo consultas de lectura, valida vehículos/posiciones y guarda el resultado privado en `data/live-result.json`.

`PROVIDER=simulator` permite desarrollar sin Satrack. La contraseña `invalida` produce `AUTH_FAILED` y `captcha` produce `CAPTCHA_REQUIRED`. El scraper real informa captcha/2FA cuando aparecen; requiere verificación manual. Ante cambios del portal conserva evidencia privada en `DATA_DIR/failures/` durante siete días.
