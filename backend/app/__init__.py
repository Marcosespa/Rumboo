"""Backend de Rumboo: monolito modular con un módulo por dominio. Ver backend/PLAN.md §3.

Cada módulo (acceso, operacion, satelital, documentos, mensajeria, monitoreo, indicadores, auditoria) es dueño
de sus tablas y expone `servicio` y `schemas`. core es infraestructura sin dominio. app/main.py es la raíz de
composición: el único lugar que conecta módulos entre sí. agentes es la capa más alta y nadie la importa.
import-linter verifica estas fronteras (pyproject.toml).
"""
