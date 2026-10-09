"""Operación: dueño de conductores, vehículos, viajes y remesas.

Casos de uso públicos con DTO: alta, reservas, consentimiento y transiciones.
Publica viaje_registrado en la misma transacción mediante core.eventos.
Satelital verifica la placa mediante su consumidor persistido. app.consultas
combina identidad operativa y estado satelital por lotes, por instancia.
No conoce proveedores ni almacena presencia o última posición satelital.
excel.py traduce la plantilla .xlsx a filas; import_trips crea un viaje por
manifiesto en su propia transacción, sin tocar el consentimiento existente.
"""
