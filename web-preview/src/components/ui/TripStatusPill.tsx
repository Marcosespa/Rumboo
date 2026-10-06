import { CalendarClock, CheckCircle2, Clock3, Truck, XCircle, type LucideIcon } from 'lucide-react'
import type { TripState } from '../../api/types'
import { Pill, type PillTone } from './Pill'

interface StateMeta {
  label: string
  tone: PillTone
  icon: LucideIcon
}

/** Estado del viaje → texto, color e icono (web/PLAN.md §4). */
export const TRIP_STATE_META: Record<TripState, StateMeta> = {
  registrado: { label: 'Sin verificar', tone: 'warning', icon: Clock3 },
  programado: { label: 'Programado', tone: 'info', icon: CalendarClock },
  en_ruta: { label: 'En ruta', tone: 'primary', icon: Truck },
  entregado: { label: 'Entregado', tone: 'success', icon: CheckCircle2 },
  cancelado: { label: 'Cancelado', tone: 'neutral', icon: XCircle },
}

/** Texto visible de cada estado, para chips de filtro y mensajes. */
export const TRIP_STATE_LABEL: Record<TripState, string> = {
  registrado: TRIP_STATE_META.registrado.label,
  programado: TRIP_STATE_META.programado.label,
  en_ruta: TRIP_STATE_META.en_ruta.label,
  entregado: TRIP_STATE_META.entregado.label,
  cancelado: TRIP_STATE_META.cancelado.label,
}

const UNKNOWN: StateMeta = { label: 'Por revisar', tone: 'neutral', icon: Clock3 }

export interface TripStatusPillProps {
  /** Estado del viaje tal como lo entrega la API. Un valor desconocido se muestra como "Por revisar". */
  state: TripState
  className?: string
}

/** Pill del estado de un viaje: siempre color + icono + texto. */
export function TripStatusPill({ state, className }: TripStatusPillProps) {
  const meta = TRIP_STATE_META[state] ?? UNKNOWN
  return (
    <Pill tone={meta.tone} icon={meta.icon} className={className}>
      {meta.label}
    </Pill>
  )
}
