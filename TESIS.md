# Rumboo — Tesis de negocio y diferenciación

Proyecto Rumboo. Documento estratégico actualizado el 5 de octubre de 2026.

## 1. Tesis central

> **Ayudamos a tu equipo de tráfico a recuperar, revisar y cerrar los cumplidos con menos trabajo manual, integrándonos con sus herramientas actuales.**

Rumboo convierte nuestro conocimiento de la operación transportadora en un sistema que acompaña cada viaje, gestiona sus novedades y consigue los documentos e información necesarios para cerrarlo. La ventaja se demuestra en viajes correctamente cerrados, tiempo ahorrado y menos pendientes.

La tesis parte de la convicción del equipo de que su conocimiento del mercado permite identificar mejor los problemas cotidianos y diseñar una solución que encaje en la operación. Ese conocimiento debe expresarse en decisiones de producto, facilidad de adopción y resultados verificables. La evidencia competitiva se construirá con clientes y pilotos.

El proyecto tiene utilidad potencial y es técnicamente viable. La viabilidad comercial se validará demostrando cuánto trabajo se ahorra, cuánto cuesta prestar el servicio y qué transportadoras están dispuestas a pagar y renovar.

La visión funcional está en [IDEA.md](IDEA.md) y el diseño técnico inicial en [IMPLEMENTACION.md](IMPLEMENTACION.md). Las mejoras estratégicas de este documento se incorporarán a las reglas técnicas conforme se concrete el piloto.

## 2. Problema, utilidad y resultado esperado

El problema que buscamos validar es una operación repartida entre satelital, llamadas, WhatsApp, Excel y documentos. El equipo de tráfico consulta ubicaciones, pide novedades, persigue cumplidos, revisa información y mantiene pendientes abiertos hasta poder cerrar el viaje.

El mayor valor esperado está en conectar ese trabajo: recuperar el documento, asociarlo a la remesa correcta, identificar faltantes, gestionar excepciones y preparar el cierre. El seguimiento aporta contexto al mismo proceso.

| Beneficio | Valor para la transportadora | Evidencia necesaria |
|---|---|---|
| Automatizar seguimiento y reportes | Menos consultas y llamadas manuales | Tiempo ahorrado al coordinador |
| Recuperar y revisar cumplidos | Menos documentos pendientes y reprocesos | Menor demora entre entrega y documento completo |
| Preparar el cierre RNDC | Menos digitación y mejor control de vencimientos | Registros correctos y menos pendientes vencidos |

La IA interpreta mensajes, audios y documentos. Las validaciones y acciones oficiales requieren reglas explícitas y aprobación humana en el MVP. Esta separación permite automatizar tareas manteniendo trazabilidad y control sobre el cierre.

## 3. Mercado y cliente inicial

MinTransporte reportó que durante 2025 participaron **2.620 empresas** y se generaron **más de 13 millones de manifiestos**. Es una referencia del volumen de actividad; la porción del mercado que podemos atender y captar requiere validación comercial. [Balance oficial de 2025](https://mintransporte.gov.co/publicaciones/12268/mintransporte-colombia-movilizo-mas-de-151-millones-de-toneladas-de-carga-en-2025-y-crecio-37/).

La hipótesis de cliente inicial es una transportadora con cientos de viajes mensuales, vehículos vinculados, un equipo pequeño de tráfico y dificultades recurrentes para recuperar documentos. El coordinador utiliza el producto y el gerente o propietario evalúa el ahorro y aprueba la compra.

El acceso del equipo fundador a operaciones reales puede acelerar la validación: observar el trabajo, revisar documentos con autorización del cliente y entender por qué un viaje permanece pendiente. Estas observaciones se convertirán en reglas configurables y flujos reutilizables entre transportadoras.

## 4. Competencia y posición comercial

Existen proveedores que anuncian funcionalidades similares. SmartQuick publica agentes de voz para conductores, OCR de cumplidos y monitoreo; FESTCAR publica gestión de remesas, manifiestos, cumplidos e integración GPS. Estas referencias describen sus ofertas públicas; no constituyen una verificación de su desempeño. [SmartQuick AI Tower](https://smartquick.ai/ai-tower.html), [FESTCAR](https://festcar.co/).

La diferenciación de Rumboo se construirá mediante una implementación sencilla, calidad del cierre, gestión de excepciones y un conocimiento operativo reflejado en el producto. La presencia de agentes de IA por sí sola aporta poca defensa competitiva.

La propuesta comercial debe explicar qué trabajo resuelve y cómo se mide: menos tiempo persiguiendo documentos, más viajes con expediente completo y menos pendientes que requieren intervención del coordinador.

## 5. Diferenciadores que queremos construir

Las siguientes capacidades son objetivos de producto e hipótesis de diferenciación. Su desempeño se validará con clientes. Cada una tiene un resultado observable y puede desarrollarse de forma gradual.

### 5.1. Gestión de excepciones hasta su resolución

Cada novedad debe tener contexto, una acción siguiente, un responsable y seguimiento. El sistema mantiene visible qué falta para avanzar el viaje y registra qué se hizo para resolverlo.

Ejemplo: llega una foto ilegible; se solicita una nueva imagen, se verifica su asociación a la remesa y se presenta al operador para revisión. Una discrepancia de peso queda identificada y asignada para aclaración. La bandeja muestra el estado de resolución de cada caso.

La primera versión cubre faltantes documentales y seguimiento de novedades dentro del alcance autorizado. La intervención con clientes externos se desarrolla en la fase futura descrita en la sección 10.

**Medición:** tiempo de resolución, intervenciones humanas por caso y porcentaje de excepciones resueltas dentro del plazo acordado.

### 5.2. Memoria operativa por cliente y destino

Guardar requisitos documentales confirmados, contactos autorizados, instrucciones de acceso, puntos de control y dificultades recurrentes. La información tendrá origen, fecha de actualización y un responsable que pueda corregirla.

Esta memoria empieza con configuraciones sencillas y observaciones verificadas. El uso permitirá mejorar instrucciones, recordatorios y preparación del expediente. La información disponible determina el nivel de personalización; los agentes deben pedir aclaración cuando falten datos.

**Medición:** reprocesos por destino, tiempo de revisión y uso efectivo de las instrucciones confirmadas.

### 5.3. Una experiencia útil para el conductor

Recibir fotos y audios, confirmar qué información llegó y pedir únicamente lo que falta. El conductor debe entender por qué se le contacta y qué necesita enviar para avanzar.

La frecuencia de contacto se medirá con la transportadora. Evitar solicitudes repetidas y permitir retomar una conversación ayuda a reducir fricción. Los contactos deben contemplar disponibilidad y condiciones seguras para responder.

**Medición:** respuesta a solicitudes, tiempo de recuperación documental, contactos repetidos y aceptación del conductor.

### 5.4. Expediente completo por viaje

Reunir documentos, novedades, aprobaciones y radicados en un expediente trazable. Mostrar qué impide cerrar cada remesa o manifiesto y cuál es la acción siguiente.

Se distinguirán el documento recibido, el expediente revisado y el registro confirmado en RNDC. En una evolución posterior, la información podrá facilitar la preparación de facturación en el sistema del cliente. El estado de cobro requiere confirmación del sistema responsable.

**Medición:** porcentaje de expedientes completos, tiempo de cierre y causas de bloqueo más frecuentes.

### 5.5. Adopción dentro de las herramientas actuales

Empezar con Excel, WhatsApp y el satelital que ya usa la transportadora, con poca configuración y sin exigir una aplicación al conductor. El piloto se centrará en un flujo y una operación concretos.

**Medición:** tiempo hasta el primer viaje gestionado, esfuerzo de configuración y trabajo necesario para incorporar una segunda transportadora.

### 5.6. Ahorro y costos visibles

Mostrar el trabajo manual ahorrado, la demora documental y los pendientes vencidos, junto con el costo de atención por viaje. Las mediciones se compararán con una línea base de la misma operación.

La combinación de gestión de excepciones y memoria operativa es una hipótesis central de ventaja acumulativa: cada caso resuelto puede mejorar las instrucciones y reglas para los siguientes viajes. Se mantendrán configuraciones reutilizables para que el crecimiento sea repetible entre clientes.

## 6. Primer MVP e integraciones

**Decisión de alcance: mantener el scraper de Satrack y OpenWA para el primer approach.** La API oficial de Satrack y la API oficial de WhatsApp se incorporarán en una evolución futura.

| Componente | Primer MVP | Evolución futura |
|---|---|---|
| Satrack | Scraper con detección de fallos y antigüedad de la ubicación | API oficial, sujeto a acceso, cobertura y condiciones comerciales |
| WhatsApp | OpenWA, recuperación de sesión y conservación de pendientes | WhatsApp Business Platform |
| Voz | Contacto al conductor según reglas y configuración del piloto | Contacto con clientes y gestión más amplia de casos |
| RNDC | Preparación o transmisión con aprobación humana y confirmación | Mayor automatización según calidad demostrada y alcance autorizado |

Satrack publica APIs e integraciones con sistemas de clientes. Esta disponibilidad es una alternativa para la evolución del producto; falta confirmar sus condiciones para el caso de Rumboo. [Satrack Developers](https://developer.satrack.com/), [Integraciones de Satrack](https://satrack.com/co/compania/integraciones/).

La migración futura a WhatsApp Business Platform deberá contemplar plantillas fuera de la ventana de atención de 24 horas y una vía clara de escalamiento humano. [Política de WhatsApp Business](https://whatsappbusiness.com/policy/).

El recorrido del MVP será:

**Registrar → monitorear → contactar → gestionar novedades → recuperar documentos → revisar → aprobar → preparar o transmitir el cumplido.**

El núcleo a validar primero es la recuperación y revisión documental hasta el cierre. El seguimiento y las conversaciones se incorporan al mismo flujo para aportar contexto y facilitar la resolución.

Un MVP de nivel San Francisco se plantea aquí como una operación real puesta a funcionar pronto, un alcance concreto y ciclos cortos de aprendizaje. El resultado esperado es que el coordinador termine el día con más viajes correctamente cerrados y menos trabajo pendiente.

## 7. Viabilidad técnica y precisión del cierre

Las tecnologías planteadas permiten construir el producto. La viabilidad operativa dependerá de la estabilidad de las integraciones, la calidad de los datos y el trabajo humano que siga requiriendo cada viaje. La documentación y el prototipo de extracción disponibles aún requieren validación de ejecución, precisión y costos en una operación real.

Los puntos que deben concretarse antes del piloto son:

1. **Scraper observable:** detectar fallos de consulta y distinguirlos de una ubicación antigua del vehículo. Mostrar cuándo el seguimiento está degradado y conservar los pendientes.
2. **OpenWA recuperable:** detectar desconexiones, recuperar la sesión y mantener las solicitudes que aún necesitan envío o respuesta.
3. **Estados operativos precisos:** distinguir llegada al destino, entrega confirmada y salida del descargue. Entrar a una geocerca puede corresponder a una espera; el seguimiento debe cubrir el descargue. Detectar una firma o sello en una foto requiere revisión de contexto y no demuestra su autenticidad.
4. **Datos suficientes para el cierre:** la guía oficial establece cumplir primero las remesas y después el manifiesto, incorporando información definitiva de Rumbooción. Esos datos pueden importarse del sistema existente o solicitarse al operador; su origen debe quedar definido. [Guía oficial de cumplidos](https://plc.mintransporte.gov.co/LinkClick.aspx?fileticket=5p1XChTx8sw%3D&mid=485&portalid=0&tabid=90).
5. **Rol de monitoreo definido:** reportar tiempos logísticos como empresa de monitoreo requiere un proceso específico de usuarios y autorizaciones. Debe definirse si Rumboo se integra con un proveedor existente o asume ese rol en una fase posterior. [Guía de monitoreo de flota](https://plc.mintransporte.gov.co/LinkClick.aspx?fileticket=Gjs6KOxRhew%3D&mid=485&portalid=0&tabid=90).

El indicador del 20 % necesita precisión: el manual operativo considera cumplidos pendientes con más de cinco días hábiles, con referencias específicas para contar el plazo. El cálculo deberá contrastarse con el listado oficial del cliente. El plazo de pago al titular y el indicador de pendientes requieren reglas diferenciadas. [Resolución y manual RNDC, apartado de expedición de manifiestos](https://mintransporte.gov.co/info/mintransporte/media/anexos/dx2Es4bu.pdf).

La continuidad ante fallas externas es parte del diseño del piloto. El Ministerio activó un plan de contingencia RNDC el 18 de septiembre de 2026; esa comunicación acredita que se requieren mecanismos para conservar y reconciliar pendientes. Este documento no presupone que la contingencia siga activa. [Comunicación oficial](https://mintransporte.gov.co/publicaciones/12418/ministerio-de-transporte-activa-plan-de-contingencia-del-rndc/).

## 8. Economía por viaje y modelo comercial

Las llamadas cada hora pueden elevar el costo y la fricción con el conductor. El piloto debe medir qué contactos aportan información y comparar la frecuencia configurada con contactos motivados por novedades o hitos relevantes.

Como referencia consultada el 5 de octubre de 2026, Retell publica US$0,07–0,31 por minuto para agentes de voz y Twilio US$0,0377 por minuto hacia móviles colombianos. El costo final depende de configuración e integración. [Retell](https://www.retellai.com/pricing), [Twilio Colombia](https://www.twilio.com/en-us/voice/pricing/co).

Con un **supuesto ilustrativo de US$0,15 por minuto total**, llamadas de un minuto y viajes de doce horas, sin omisiones ni reintentos:

| Estrategia | Voz por viaje | Voz para 500 viajes |
|---|---:|---:|
| Doce llamadas | US$1,80 | US$900 |
| Dos llamadas | US$0,30 | US$150 |

Este cálculo cubre voz. El costo de prestar el servicio también incluye mensajes, documentos, infraestructura, reintentos y soporte humano. Las llamadas de dos minutos duplican el componente ilustrado. El trabajo humano pendiente por viaje debe medirse explícitamente.

La hipótesis de cobro es una tarifa base mensual más volumen de viajes gestionados, con límites de voz e implementación cobrada cuando corresponda. La disposición a pagar se determinará con propuestas y pilotos pagados.

Para crecer de manera rentable, la incorporación de clientes debe aprovechar configuraciones e integraciones reutilizables. Se medirán margen por cliente y tiempo de soporte para identificar operaciones que requieren demasiado trabajo específico.

## 9. Validación y criterios para avanzar

El primer compromiso comercial es hablar con 8–10 transportadoras y buscar **dos pilotos pagados**. Las conversaciones deben explorar viajes recientes, documentos pendientes, tiempo invertido y herramientas actuales.

Cada piloto tendrá una línea base de trabajo manual por viaje, demora documental, errores, pendientes y costo de atención. Se empezará en sombra y se pasará a una operación asistida con revisión humana.

| Dimensión | Medición |
|---|---|
| Productividad | Minutos de trabajo manual por viaje |
| Documentación | Tiempo desde entrega hasta documento completo |
| Cierre | Tiempo hasta confirmación RNDC y pendientes vencidos |
| Calidad | Errores críticos, correcciones y reprocesos |
| Adopción | Respuesta del conductor y uso del coordinador |
| Economía | Costo total por viaje, margen y soporte por cliente |
| Valor comercial | Pago del piloto y disposición a renovar |

Como criterios iniciales propuestos, se buscará una reducción de al menos **30 % del trabajo manual**, una mejora clara del cierre y clientes dispuestos a renovar. Estas metas requieren medición; no se presentan como resultados alcanzados.

La decisión de ampliar el producto se apoyará en un flujo repetible, integraciones suficientemente estables y un costo de soporte compatible con el precio que el cliente acepta pagar.

## 10. Visión futura: agentes que avanzan la resolución cuando tú no estás

> **Cuando tú no estés, nuestros agentes de IA podrán contactar al cliente por llamada y mensajes, recopilar información, gestionar faltantes y avanzar la resolución de problemas hasta dejar el caso listo para tu revisión y aprobación final.**

Esta capacidad pertenece a una etapa posterior al MVP. Amplía la asistencia al conductor hacia la coordinación con el cliente o destinatario de la carga, dentro del alcance que autorice la transportadora.

El recorrido futuro será:

**Problema detectado → contacto con el cliente → aclaración y recuperación de información → preparación de la solución → revisión y aprobación final humana → ejecución y confirmación.**

Ejemplo: un viaje tiene un documento pendiente. El agente revisa qué falta, llama al contacto autorizado del cliente, solicita el soporte, registra la respuesta, verifica su asociación al viaje y deja el expediente preparado para el último paso de revisión humana. Si el caso requiere una decisión, presenta la información disponible y una propuesta para que el responsable pueda aprobarla.

Los agentes podrán dar seguimiento a compromisos y reunir información mientras el equipo humano está ausente. Los casos que requieran intervención humana se escalarán con el contexto completo; la revisión final incluirá qué ocurrió, qué gestiones se realizaron, qué evidencia se obtuvo y qué decisión queda pendiente.

Esta visión se desarrollará después de validar la calidad del flujo de cumplidos, los contactos autorizados y el costo de atención. Las APIs oficiales de Satrack y WhatsApp forman parte de la evolución futura de las integraciones, con su alcance y orden definidos por las necesidades de la operación.
