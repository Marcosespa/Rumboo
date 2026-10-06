import { cn } from '../../lib/cn'
import { plate } from '../../lib/format'

export interface PlateProps {
  /** Placa tal como llega ("wln482", "WLN 482"…). Se muestra como "WLN 482". */
  value: string
  className?: string
}

/** Placa del vehículo: mayúsculas, tracking amplio y cifras tabulares. */
export function Plate({ value, className }: PlateProps) {
  return (
    <span className={cn('inline-block whitespace-nowrap rounded-chip border border-line-strong bg-paper px-2 py-0.5 text-sm font-semibold uppercase tracking-wide tabular text-ink', className)}>
      {plate(value)}
    </span>
  )
}
