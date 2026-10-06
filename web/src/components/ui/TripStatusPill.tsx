import { CalendarClock, CheckCircle2, Clock3, Truck, XCircle, type LucideIcon } from 'lucide-react'
import type { TripState } from '../../api/types'
import { useI18n, type MessageKey } from '../../i18n'
import { Pill, type PillTone } from './Pill'

interface StateMeta {
  tone: PillTone
  icon: LucideIcon
}

/** Estado del viaje → color e icono (web/PLAN.md §4). El texto sale del diccionario: `status.trip.<estado>`. */
export const TRIP_STATE_META: Record<TripState, StateMeta> = {
  registrado: { tone: 'warning', icon: Clock3 },
  programado: { tone: 'info', icon: CalendarClock },
  en_ruta: { tone: 'primary', icon: Truck },
  entregado: { tone: 'success', icon: CheckCircle2 },
  cancelado: { tone: 'neutral', icon: XCircle },
}

/** Estados en el orden de la bandeja (chips de filtro, conteos). */
export const TRIP_STATES: TripState[] = ['registrado', 'programado', 'en_ruta', 'entregado', 'cancelado']

/** Clave de diccionario del texto de un estado: `t(tripStateKey('en_ruta'))` → "En ruta" / "On route". */
export const tripStateKey = (state: TripState): MessageKey => `status.trip.${state}`

const UNKNOWN: StateMeta = { tone: 'neutral', icon: Clock3 }

export interface TripStatusPillProps {
  /** Estado del viaje tal como lo entrega la API. Un valor desconocido se muestra como "Por revisar". */
  state: TripState
  className?: string
}

/** Pill del estado de un viaje: siempre color + icono + texto (traducido). */
export function TripStatusPill({ state, className }: TripStatusPillProps) {
  const { t } = useI18n()
  const known = state in TRIP_STATE_META
  const meta = known ? TRIP_STATE_META[state] : UNKNOWN
  return (
    <Pill tone={meta.tone} icon={meta.icon} className={className}>
      {t(known ? tripStateKey(state) : 'status.trip.unknown')}
    </Pill>
  )
}
