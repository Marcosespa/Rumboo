import type { ReactNode } from 'react'
import { cn } from '../../lib/cn'

export interface MetricProps {
  label: ReactNode
  value: ReactNode
  className?: string
}

/** Tile translúcido de métrica para usar dentro de `HeroPanel`. */
export function Metric({ label, value, className }: MetricProps) {
  return (
    <div className={cn('rounded-subcard border border-paper/12 bg-paper/8 px-3 py-4', className)}>
      <p className="m-0 text-xs uppercase tracking-[0.16em] opacity-55">{label}</p>
      <p className="m-0 mt-2 text-base font-semibold">{value}</p>
    </div>
  )
}
