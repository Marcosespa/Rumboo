"""Backend de Rumboo: monolito modular con un módulo por dominio. Ver backend/PLAN.md §3.

Cada módulo (acceso, operacion, satelital, documentos, mensajeria, monitoreo, voz, indicadores, auditoria) es
dueño de sus tablas y expone `servicio` y `schemas`. core es infraestructura sin dominio. app/main.py es la raíz de
composición: el único lugar que conecta módulos entre sí; app/consultas.py combina DTO de varios módulos por
instancia. Los agentes de audio viven en voz-service/. import-linter verifica estas fronteras (pyproject.toml).
"""
