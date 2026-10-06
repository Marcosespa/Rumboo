import type { ReactNode } from 'react'
import type { LucideIcon } from 'lucide-react'
import { cn } from '../../lib/cn'

export interface StatTileProps {
  /** Icono Lucide en primary, p. ej. `Clock3`, `CalendarClock`. */
  icon: LucideIcon
  title: ReactNode
  /** Valor o conteo, en mist (p. ej. "3 viajes"). */
  value: ReactNode
  className?: string
}

/** Tile claro de dato: icono + título arriba, valor en mist abajo. Va en grillas de 2–4 columnas. */
export function StatTile({ icon: Icon, title, value, className }: StatTileProps) {
  return (
    <div className={cn('rounded-subcard border border-line/70 bg-paper/80 px-3 py-4', className)}>
      <div className="flex items-center gap-2 text-primary">
        <Icon size={16} aria-hidden="true" />
        <p className="m-0 text-base font-semibold text-ink">{title}</p>
      </div>
      <p className="m-0 mt-2 text-base leading-relaxed text-mist">{value}</p>
    </div>
  )
}
