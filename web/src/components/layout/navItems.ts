import type { MessageKey } from '../../i18n'
import { ChartColumn, ClipboardList, PlusCircle, Settings, Truck, type LucideIcon } from 'lucide-react'

export interface NavItem {
  to: string
  /** Clave del diccionario (`nav.*`). */
  labelKey: MessageKey
  icon: LucideIcon
  /** NavLink `end`: solo activo con la ruta exacta (evita que "Viajes" quede activo en /viajes/nuevo). */
  end?: boolean
}

/** Los cinco destinos de la bandeja (web/PLAN.md): barra lateral ≥ 860px, barra inferior debajo. */
export const NAV_ITEMS: NavItem[] = [
  { to: '/', labelKey: 'nav.panel', icon: ChartColumn, end: true },
  { to: '/viajes', labelKey: 'nav.trips', icon: ClipboardList, end: true },
  { to: '/viajes/nuevo', labelKey: 'nav.newTrip', icon: PlusCircle },
  { to: '/flota', labelKey: 'nav.fleet', icon: Truck },
  { to: '/ajustes', labelKey: 'nav.settings', icon: Settings },
]
