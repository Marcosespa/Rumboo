import type { ReactNode } from 'react'
import type { LucideIcon } from 'lucide-react'
import { cn } from '../../lib/cn'

/**
 * Colores de pill de la skill (`.r-pill--*`) más tres tonos para los estados de la bandeja:
 * `info` (primary-subtle/primary), `primary` (relleno azul) y `neutral` (cloud-soft/mist).
 */
export type PillTone =
  | 'ok'
  | 'attention'
  | 'critical'
  | 'criticalSolid'
  | 'success'
  | 'warning'
  | 'accent'
  | 'info'
  | 'primary'
  | 'neutral'

const TONE: Record<PillTone, string> = {
  ok: 'bg-paper text-mist',
  attention: 'bg-primary-subtle text-primary',
  critical: 'bg-error-subtle text-error',
  criticalSolid: 'bg-error text-paper',
  success: 'bg-success-subtle text-success',
  warning: 'bg-warning-subtle text-warning-text',
  accent: 'bg-accent-subtle text-accent-dark',
  info: 'bg-primary-subtle text-primary',
  primary: 'bg-primary text-on-primary',
  neutral: 'bg-cloud-soft text-mist',
}

export interface PillProps {
  tone: PillTone
  /** Icono Lucide a 12px antes del texto (estados = color + icono + texto). */
  icon?: LucideIcon
  children: ReactNode
  className?: string
}

/** Base de las pills de estado: `StatusPill`, `TripStatusPill` y `SatrackStatusPill` se construyen sobre ella. */
export function Pill({ tone, icon: Icon, children, className }: PillProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 whitespace-nowrap rounded-pill px-3 py-1 text-[12px] font-semibold leading-body',
        TONE[tone],
        className,
      )}
    >
      {Icon && <Icon size={12} aria-hidden="true" />}
      {children}
    </span>
  )
}
