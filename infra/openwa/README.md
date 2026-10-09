# OpenWA · WhatsApp

Responsabilidad: conectar WhatsApp para pedir y recibir datos del conductor. Es un servicio externo; Rumboo lo consumirá desde `backend/app/mensajeria/openwa.py`.

Integración pendiente de M3. Antes de habilitarla se debe fijar imagen/revisión, autenticación, contrato real de envío y webhooks, persistencia de sesión y mecanismo de reconciliación. No se presupone que OpenWA admita una cabecera de idempotencia o una firma específica.

El backend decide destinatario, consentimiento y relación conductor/viaje; guarda la intención antes del envío y deduplica las respuestas por ID externo. La sesión WhatsApp y su almacenamiento pertenecen a OpenWA. Sin acceso a las tablas de Rumboo ni secretos en Git.

No se añade a Compose hasta verificar este contrato y completar sus pruebas con un cliente falso.
