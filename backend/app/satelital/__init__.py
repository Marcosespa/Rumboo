"""Satelital: cuenta, consultas, posiciones y vehiculos_satelitales.

Credenciales cifradas, una reserva pendiente por cuenta, flota completa y resultados
persistidos. Callback y GET convergen en apply_result idempotente. Los jobs se
reservan antes del POST y se recuperan sin depender de una petición HTTP.
cliente.py concentra el HTTP externo; enlaces.py declara consumidores y tareas.
Usa DTO y operaciones públicas de operación; cada módulo escribe sus tablas.
"""
