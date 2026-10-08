"""Agentes de IA del negocio. Ninguno está implementado todavía (voz, extracción y RNDC están pendientes).

Un agente es un CLIENTE de los módulos, igual que un router: no es dueño de reglas de negocio ni de tablas
ajenas. Por eso está en la capa más alta y ningún módulo lo importa.

Estructura prevista (se crea con el primer agente; sin código simulado antes):

    agentes/
    ├── llm.py            ÚNICO archivo que conoce el SDK del proveedor de IA. Modelo configurable por agente.
    ├── herramientas.py   Herramienta = nombre, descripción, schema Pydantic de entrada y la función de servicio
    │                     que ejecuta. Valida argumentos, ejecuta, audita. No es un framework genérico.
    ├── models.py         acciones_agente: herramienta, argumentos validados, resultado, error, contexto.
    └── <nombre_agente>/  Uno por agente, p. ej. voz_conductor/, clasificador_mensajes/, extraccion_cumplidos/
        ├── instrucciones.md  Prompt versionado en Git.
        ├── contexto.py       Arma el contexto desde servicios (viaje, conductor, novedades). Lo inyecta el
        │                     servidor; el agente nunca elige transportadora ni viaje.
        ├── herramientas.py   Lista FIJA de herramientas; cada una llama a `<modulo>.servicio`.
        └── agente.py         Une contexto + llm + herramientas y registra cada acción.

Reglas (import-linter verifica las de importación):
1. Solo usa `<modulo>.servicio` y `<modulo>.schemas`: pasa las mismas validaciones y el mismo aislamiento por
   transportadora que la API HTTP. Nunca toca modelos ni SQL directamente.
2. Las herramientas no reciben `transportadora_id` ni ids libres: el contexto del servidor los fija.
3. Acciones solo humanas (aprobar o rechazar cumplidos, transmitir al RNDC) viven en módulos que app.agentes
   tiene prohibido importar (p. ej. `documentos.revision`).
4. Se activan por eventos (core.eventos) o tareas (core.tareas) enlazados en app/main.py, nunca porque un
   módulo de negocio los llame.
5. Cada llamada a herramienta queda en acciones_agente y en auditoria.
6. Sin catálogo dinámico, agentes anidados, suspensiones genéricas ni varios LLM activos a la vez.
7. El transporte en tiempo real (audio de llamadas) irá en un microservicio `voz-service`; la decisión y las
   herramientas quedan aquí, porque necesitan transacciones con los datos del negocio.
8. Se prueban con un LLM falso: las herramientas son funciones deterministas.

Agentes previstos: voz al conductor (consultar viaje, registrar novedad, actualizar ETA, solicitar seguimiento),
clasificador de mensajes de WhatsApp (proponer viaje y novedad para revisión humana) y extracción de cumplidos
(proponer datos declarados con origen "ia"; nunca aprobar).
"""
