# voz-service · agentes de audio

Responsabilidad: manejar agentes de audio y conversaciones con el conductor. Servicio pendiente; este directorio documenta su frontera y no contiene un servicio ejecutable.

Aquí vivirán las sesiones conversacionales, prompts y adaptadores del proveedor de voz/IA. El backend enviará contexto limitado de conductor/viaje, después de validar contacto y consentimiento. Los resultados y solicitudes de acciones volverán a la API autenticada del backend; el backend validará y auditará cada efecto.

No accede a PostgreSQL de Rumboo ni decide estados operativos, aprobación de documentos o transmisión RNDC. El futuro adaptador del backend pertenece a `backend/app/voz/cliente.py`.

Antes de implementar: elegir proveedor/modelos, fijar contratos de inicio/estado/resultados, autenticación, límites y comportamiento ante una conexión interrumpida. No se habilitan endpoints ni se incorpora a Compose hasta completar esos pasos.
