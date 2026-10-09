"""Consultas compuestas por aplicación: combina DTO sin compartir modelos ni registros globales."""
from app.operacion import servicio as operacion
from app.satelital import servicio as satelital
from app.satelital.schemas import EstadoVehiculoDTO
from app.indicadores import servicio as indicadores


class ConsultasOperacion:
    def _trips(self, db, tenant, trips, detail=False):
        states = satelital.vehicle_states(db, tenant, [t.vehiculo.id for t in trips])
        result = []
        for trip in trips:
            fields = trip.model_dump(exclude={"remesas", "eventos"})
            fields["vehiculo"].update(states.get(trip.vehiculo.id, EstadoVehiculoDTO()).model_dump())
            if detail:
                fields["remesas"] = [r.model_dump() for r in trip.remesas]
                fields["eventos"] = list(trip.eventos)
            result.append(fields)
        return result

    def trip(self, db, tenant, trip_id):
        return self._trips(db, tenant, [operacion.get_trip(db, tenant, trip_id)], detail=True)[0]

    def trips(self, db, tenant, state, text, page, page_size):
        result = operacion.list_trips(db, tenant, state, text, page, page_size)
        result["items"] = self._trips(db, tenant, result["items"])
        return result

    def vehicles(self, db, tenant, page, page_size):
        result = operacion.list_vehicles(db, tenant, page, page_size)
        states = satelital.vehicle_states(db, tenant, [v.id for v in result["items"]])
        result["items"] = [v.model_dump() | states.get(v.id, EstadoVehiculoDTO()).model_dump() for v in result["items"]]
        return result

    def panel(self, db, tenant):
        result = indicadores.panel(db, tenant)
        result["viajes_activos"] = self._trips(db, tenant, result["viajes_activos"])
        return result
