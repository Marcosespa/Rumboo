import type { ReactNode } from 'react'
import { CheckCircle2, Clock3, Sparkles, TriangleAlert, type LucideIcon } from 'lucide-react'
import { Pill, type PillTone } from './Pill'

export type StatusPillStatus = 'ok' | 'attention' | 'critical' | 'success' | 'warning' | 'accent'

const PRESETS: Record<StatusPillStatus, { label: string; icon: LucideIcon; tone: PillTone }> = {
  ok: { label: 'Al día', icon: CheckCircle2, tone: 'ok' },
  attention: { label: 'Pendiente', icon: Clock3, tone: 'attention' },
  critical: { label: 'Urgente', icon: TriangleAlert, tone: 'critical' },
  success: { label: 'Pagado', icon: CheckCircle2, tone: 'success' },
  warning: { label: 'Por vencer', icon: Clock3, tone: 'warning' },
  accent: { label: 'Nuevo', icon: Sparkles, tone: 'accent' },
}

export interface StatusPillProps {
  /**
   * ok="Al día" (paper/mist) · attention="Pendiente" (primary subtle) · critical="Urgente"
   * (error subtle) · success="Pagado" · warning="Por vencer" · accent="Nuevo". @default "ok"
   */
  status?: StatusPillStatus
  /** Solo critical: fondo error sólido con texto paper. @default false */
  solid?: boolean
  /** Antepone el icono del preset. Úsalo siempre que la pill sea el único indicador de estado. @default false */
  withIcon?: boolean
  /** Texto propio; por defecto la etiqueta canónica del preset. */
  children?: ReactNode
  className?: string
}

/** Pill de estado genérica de la skill. Para viajes y Satrack usa `TripStatusPill` / `SatrackStatusPill`. */
export function StatusPill({ status = 'ok', solid = false, withIcon = false, children, className }: StatusPillProps) {
  const preset = PRESETS[status] ?? PRESETS.ok
  const tone: PillTone = solid && status === 'critical' ? 'criticalSolid' : preset.tone
  return (
    <Pill tone={tone} icon={withIcon ? preset.icon : undefined} className={className}>
      {children ?? preset.label}
    </Pill>
  )
}
