import { ChartColumn, ClipboardList, PlusCircle, Settings, Truck, type LucideIcon } from 'lucide-react'

export interface NavItem {
  to: string
  label: string
  icon: LucideIcon
  /** NavLink `end`: solo activo con la ruta exacta (evita que "Viajes" quede activo en /viajes/nuevo). */
  end?: boolean
}

/** Los cinco destinos de la bandeja (web/PLAN.md): barra lateral ≥ 860px, barra inferior debajo. */
export const NAV_ITEMS: NavItem[] = [
  { to: '/', label: 'Panel', icon: ChartColumn, end: true },
  { to: '/viajes', label: 'Viajes', icon: ClipboardList, end: true },
  { to: '/viajes/nuevo', label: 'Nuevo', icon: PlusCircle },
  { to: '/flota', label: 'Flota', icon: Truck },
  { to: '/ajustes', label: 'Ajustes', icon: Settings },
]
