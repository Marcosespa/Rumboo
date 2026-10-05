# Liquida — Monitoreo Inteligente de Viajes de Carga

> **En una frase:** agentes de IA que acompañan cada viaje de carga desde que sale hasta que se cumple en el RNDC: vigilan la ubicación del camión por satelital, hablan con el conductor por llamada y WhatsApp, informan a la transportadora y, al llegar, procesan el cumplido.

---

## 1. Qué vamos a construir

Un sistema que, para cada viaje registrado por una transportadora:

1. **Recibe los datos del viaje** (origen, destino, ruta, conductor, satelital).
2. **Monitorea la ubicación** del vehículo consultando el satelital (primero Satrack).
3. **Detecta desvíos, paradas largas o retrasos** contra la ruta planificada.
4. **Se comunica con el conductor**: llamada cada hora y mensajes por WhatsApp.
5. **Informa a la transportadora** con un resumen cada 3 horas y alertas inmediatas cuando algo anda mal.
6. **Cierra el viaje**: recibe la foto del cumplido por WhatsApp, la valida y prepara/transmite el cumplido al RNDC.

### Por qué importa
- **Resolución 20263040016075 de 2026:** si los cumplidos pendientes superan el **20%** de los manifiestos de los últimos 30 días, el RNDC **bloquea nuevos manifiestos**. Cerrar rápido los cumplidos protege la operación.
- **Decreto 1017 de 2025:** el saldo al propietario se debe pagar en máximo **5 días hábiles**; eso exige tener el cumplido a tiempo.
- Hoy el seguimiento y el cierre se hacen a mano entre WhatsApp, llamadas y Excel.

---

## 2. Alcance del MVP

### Incluye
| Módulo | Descripción |
|---|---|
| Registro de viajes | Formulario web / carga de Excel con datos del viaje, conductor y satelital |
| Scraper de Satrack | Consulta periódica de la posición del vehículo |
| Motor de reglas de ruta | Detecta desvío, detención prolongada, retraso estimado y pérdida de señal |
| Llamadas al conductor | Agente de voz cada hora para pedir novedades |
| WhatsApp (OpenWA) | Mensajes al conductor, recepción de fotos y respuestas |
| Reportes a la transportadora | Resumen cada 3 horas + alertas inmediatas |
| Cierre de viaje | Lectura de la foto del cumplido, validación y preparación del cumplido RNDC |
| Bandeja web | Panel para ver viajes en curso, alertas y aprobar cumplidos |

### No incluye (por ahora)
- **Fase 1 – Agente de correo** que extrae propuestas de viaje (se pospone).
- API oficial de WhatsApp de Meta (se usa OpenWA en el MVP).
- Liquidación del viaje (flete − anticipo − descuentos), pagos y facturación.
- Satelitales distintos a Satrack.
- App para conductores.

---

## 3. Actores

- **Transportadora:** registra viajes, recibe reportes, aprueba cumplidos.
- **Conductor:** recibe llamadas y mensajes, reporta novedades, envía el cumplido.
- **Agente de IA:** monitorea, conversa, interpreta respuestas y fotos.
- **Operador humano (de la transportadora):** atiende excepciones desde la bandeja.

---

## 4. Flujo de un viaje (end-to-end)

```
[Registro] → [Programado] → [En ruta] ⇄ [Con novedad] → [Entregado] → [Cumplido pendiente] → [Cumplido RNDC] → [Cerrado]
```

**Ejemplo:**
> La transportadora registra el manifiesto 12345 Bogotá → Cali con placa ABC123 y su usuario de Satrack → al iniciar, el sistema consulta Satrack cada 5 min → a la hora, el agente llama al conductor: *"¿Cómo va el viaje, alguna novedad?"* → a las 3 horas, la transportadora recibe un resumen → el camión lleva 90 min detenido fuera de ruta → alerta inmediata + WhatsApp al conductor → el conductor responde "pinchazo, ya seguimos" → se registra la novedad → al llegar a Cali, el agente pide la foto del cumplido → la lee, compara el peso con la remesa → una persona aprueba con un clic → se transmite el cumplido al RNDC y se notifica a la transportadora.

---

## 5. Fases de implementación

### Fase 2 — Carga inicial de datos
La transportadora registra cada viaje con:

- **Viaje:** número de manifiesto y remesa(s), origen, destino, ruta planificada (o puntos de control), fecha/hora estimada de salida y llegada.
- **Carga:** descripción, **peso** (kg), cantidad de unidades, cliente/destinatario.
- **Conductor:** nombre, cédula, teléfono/WhatsApp.
- **Vehículo:** placa, propietario.
- **Satelital:** proveedor (Satrack), credenciales o acceso, identificador del dispositivo.

Canales de carga: formulario web y plantilla Excel. Validaciones: placa y cédula con formato correcto, teléfono válido, manifiesto único.

### Fase 3 — Monitoreo en tiempo real

**3.1 Ubicación (Satrack)**
- Scraper con navegador automatizado (Playwright) que inicia sesión y extrae posición, velocidad, hora del último reporte y estado.
- Frecuencia: cada 5–10 min por vehículo (configurable).
- Reutilizar sesiones y respetar límites para no ser bloqueados.
- Se guarda cada punto en el historial del viaje.

**3.2 Motor de reglas (determinístico, sin IA)**
| Regla | Condición (configurable) | Acción |
|---|---|---|
| Desvío de ruta | > X km del corredor planificado | Alerta + WhatsApp al conductor |
| Detención prolongada | Velocidad 0 por > 60 min fuera de punto autorizado | Llamada al conductor |
| Retraso | ETA > hora pactada + margen | Aviso en el reporte |
| Sin señal | Sin reporte del satelital por > 30 min | Alerta inmediata |
| Llegada | Dentro de geocerca del destino | Inicia cierre del viaje |

**3.3 Comunicación con el conductor**
- **Llamada cada hora** con agente de voz: pregunta por el estado y novedades; la respuesta se transcribe y la IA la clasifica (sin novedad, retraso, avería, accidente, problema con la carga, otro).
- Si no contesta: reintento a los 10 min → WhatsApp → alerta a la transportadora tras 2 intentos fallidos.
- **WhatsApp vía OpenWA:** mensajes del agente, recepción de texto, audios y fotos.

**3.4 Reportes a la transportadora**
- **Cada 3 horas:** resumen por viaje (ubicación, avance %, ETA, novedades).
- **Inmediato:** desvío, detención larga, sin señal, novedad grave reportada por el conductor.
- Canal: WhatsApp del coordinador + bandeja web (email opcional).

### Fase 4 — Cierre del viaje
1. Al detectar llegada, el agente pide por WhatsApp la foto del cumplido (remesa firmada y sellada).
2. Un LLM de visión extrae: número de remesa/manifiesto, firma, sello, fecha, peso o cantidades recibidas, observaciones (faltantes, averías).
3. **Validación:** el RNDC trabaja con **peso**, así que se compara el peso de salida vs. el peso entregado. Las cantidades (cajas) se registran como dato complementario.
4. Si todo cuadra → queda listo para aprobación. Si hay diferencias o falta firma/sello → excepción en la bandeja y se pide nueva foto si aplica.
5. Una persona **aprueba con un clic**.
6. Se transmite el cumplido al **RNDC** (web service) y se envía confirmación + documentos a la transportadora.

---

## 6. Arquitectura

```
                 ┌────────────────────┐
  Transportadora │  Bandeja web       │  (Next.js)
  ──────────────▶│  registro/alertas  │
                 └─────────┬──────────┘
                           │ REST
                 ┌─────────▼──────────┐       ┌───────────────┐
                 │  API (FastAPI)     │◀─────▶│  Postgres     │
                 └─────────┬──────────┘       └───────────────┘
                           │ cola de tareas
     ┌─────────────┬───────┴───────┬──────────────┬─────────────┐
┌────▼─────┐ ┌─────▼──────┐ ┌──────▼─────┐ ┌──────▼─────┐ ┌─────▼─────┐
│ Scraper  │ │ Motor de   │ │ Agente de  │ │ Servicio   │ │ Conector  │
│ Satrack  │ │ reglas +   │ │ voz        │ │ OpenWA     │ │ RNDC      │
│(Playwr.) │ │ scheduler  │ │ (llamadas) │ │ (WhatsApp) │ │ (SOAP)    │
└──────────┘ └────────────┘ └────────────┘ └────────────┘ └───────────┘
                                   │              │
                                   └──── LLM ─────┘  (clasificación + visión)
                                          │
                                   ┌──────▼──────┐
                                   │ S3 (fotos,  │
                                   │ audios)     │
                                   └─────────────┘
```

### Stack propuesto
- **Backend:** Python + FastAPI
- **Base de datos:** Postgres (+ PostGIS para rutas y geocercas)
- **Tareas programadas y colas:** Celery/RQ + Redis (o APScheduler al inicio)
- **Scraping:** Playwright
- **WhatsApp:** OpenWA (servicio Node.js aparte)
- **Voz:** proveedor de telefonía + agente de voz (por definir, ver §10)
- **IA:** LLM con visión detrás de una capa de abstracción
- **Archivos:** S3 o equivalente
- **Frontend:** Next.js

### Reglas de diseño
- **La IA interpreta, no decide sola:** clasifica respuestas y extrae datos de fotos; las alertas y validaciones las hace código determinístico.
- **Humano en el loop** para todo lo que va al RNDC durante el MVP.
- **Log inmutable** de cada evento: posición, llamada, mensaje, alerta, aprobación (quién y cuándo).
- **Cada transportadora es configuración**, no código a la medida (umbrales, horarios, contactos).
- **Integraciones intercambiables:** Satrack y OpenWA detrás de interfaces para poder agregar otros satelitales o pasar a la API de Meta.

---

## 7. Modelo de datos (inicial)

| Tabla | Campos clave |
|---|---|
| `transportadoras` | id, nombre, NIT, contactos, configuración (umbrales, frecuencias) |
| `conductores` | id, nombre, cédula, teléfono |
| `vehiculos` | id, placa, propietario, proveedor_satelital, id_dispositivo |
| `viajes` | id, manifiesto, transportadora_id, conductor_id, vehiculo_id, origen, destino, ruta (geometría), peso_salida, estado, eta |
| `remesas` | id, viaje_id, número, cliente, peso, cantidad |
| `posiciones` | viaje_id, lat, lng, velocidad, timestamp |
| `interacciones` | viaje_id, canal (llamada/whatsapp), dirección, contenido/transcripción, clasificación, timestamp |
| `alertas` | viaje_id, tipo, severidad, estado (abierta/atendida), timestamp |
| `cumplidos` | viaje_id, foto_url, datos_extraídos, peso_entregado, diferencias, aprobado_por, estado_rndc |
| `eventos` | log inmutable de todo lo anterior |

---

## 8. Plan de trabajo

| Semanas | Entregable |
|---|---|
| 1 | Confirmar acceso al **web service del RNDC** y a Satrack. Definir proveedor de voz. Setup del repo, base de datos y API |
| 2–3 | Registro de viajes (web + Excel) y **scraper de Satrack** guardando posiciones |
| 4 | Motor de reglas (desvío, detención, sin señal, llegada) y bandeja web con viajes y alertas |
| 5 | **OpenWA**: mensajes al conductor y recepción de fotos/respuestas |
| 6 | **Agente de voz**: llamadas cada hora, transcripción y clasificación |
| 7 | Reportes cada 3 horas y alertas a la transportadora |
| 8–9 | Cierre del viaje: lectura del cumplido, validación por peso, aprobación y conector RNDC |
| 10–12 | Piloto con una transportadora: primero **en sombra**, luego asistido |

---

## 9. Métricas del piloto

- % de viajes con seguimiento completo (sin huecos de señal sin atender).
- Tiempo desde una anomalía hasta la alerta a la transportadora (< 10 min).
- % de llamadas contestadas y clasificadas correctamente.
- % de cumplidos recibidos dentro de **5 días hábiles** (meta ≥ 90%).
- Precisión en campos críticos del cumplido (meta ≥ 98%).
- % de cumplidos pendientes vs. umbral del 20%.

---

## 10. Riesgos y decisiones pendientes

**Riesgos**
1. **Scraper de Satrack frágil:** cambios en la web o bloqueos rompen el monitoreo. Mitigar con alertas de fallo del scraper y buscar API oficial o acuerdo.
2. **OpenWA no es oficial:** riesgo de baneo del número. Usar números dedicados y tener plan de migración a la API de Meta.
3. **Acceso al RNDC:** si no se puede transmitir por web service con usuarios de la transportadora, el cierre queda como "preparado" para carga manual.
4. **Conductores que no contestan** o sin señal en carretera: reintentos y escalamiento.
5. **Costo de las llamadas** cada hora por viaje: medir y ajustar frecuencia.
6. **Datos personales** (Ley 1581): autorización del conductor para llamadas, grabación y ubicación.

**Decisiones pendientes**
- [ ] Proveedor de telefonía y agente de voz.
- [ ] Cómo se carga la ruta planificada (trazado en mapa, ciudades intermedias o ruta calculada automáticamente).
- [ ] Credenciales de Satrack: ¿por transportadora o por vehículo?
- [ ] Canal principal de reportes a la transportadora (WhatsApp, email o solo bandeja).
- [ ] Transportadora para el piloto.
