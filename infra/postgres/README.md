# PostgreSQL · datos de Rumboo

La instancia activa se define en `compose.yaml`, servicio `db`, imagen `postgres:16-alpine`, volumen `pg_data`. Las migraciones son propiedad de `backend/alembic/`; se ejecutan antes de arrancar la API.

Persiste los datos de negocio, posiciones, consultas y resultados, además de `entregas_pendientes`. Solo el backend accede a estas tablas. Satrack, OpenWA y voz-service devuelven sus resultados por sus contratos y conservan su propia persistencia cuando corresponda.

Los archivos de cumplidos irán en almacenamiento privado; PostgreSQL guardará sus metadatos, versiones y referencias. La implementación documental sigue pendiente.

Respaldar la BD y conservar las claves de cifrado por separado del repositorio. Validar la restauración antes de usar el despliegue en producción. Esta carpeta organiza la responsabilidad; la configuración existente permanece en Compose.

Las pruebas borran exclusivamente una BD desechable cuyo nombre termina en `_test`. Para evitar interferencias entre procesos, asignar una BD distinta a cada ejecución mediante `TEST_DATABASE_URL`.
