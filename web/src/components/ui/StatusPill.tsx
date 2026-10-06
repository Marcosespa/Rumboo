import type { ReactNode } from 'react'
import { CheckCircle2, Clock3, Sparkles, TriangleAlert, type LucideIcon } from 'lucide-react'
import { useI18n, type MessageKey } from '../../i18n'
import { Pill, type PillTone } from './Pill'

export type StatusPillStatus = 'ok' | 'attention' | 'critical' | 'success' | 'warning' | 'accent'

const PRESETS: Record<StatusPillStatus, { label: MessageKey; icon: LucideIcon; tone: PillTone }> = {
  ok: { label: 'status.pill.ok', icon: CheckCircle2, tone: 'ok' },
  attention: { label: 'status.pill.attention', icon: Clock3, tone: 'attention' },
  critical: { label: 'status.pill.critical', icon: TriangleAlert, tone: 'critical' },
  success: { label: 'status.pill.success', icon: CheckCircle2, tone: 'success' },
  warning: { label: 'status.pill.warning', icon: Clock3, tone: 'warning' },
  accent: { label: 'status.pill.accent', icon: Sparkles, tone: 'accent' },
}

export interface StatusPillProps {
  /**
   * ok="Al día" (paper/mist) · attention="Pendiente" (primary subtle) · critical="Urgente"
   * (error subtle) · success="Pagado" · warning="Por vencer" · accent="Nuevo" (etiquetas en español; en inglés se traducen). @default "ok"
   */
  status?: StatusPillStatus
  /** Solo critical: fondo error sólido con texto paper. @default false */
  solid?: boolean
  /** Antepone el icono del preset. Úsalo siempre que la pill sea el único indicador de estado. @default false */
  withIcon?: boolean
  /** Texto propio; por defecto la etiqueta canónica del preset (traducida). */
  children?: ReactNode
  className?: string
}

/** Pill de estado genérica de la skill. Para viajes y Satrack usa `TripStatusPill` / `SatrackStatusPill`. */
export function StatusPill({ status = 'ok', solid = false, withIcon = false, children, className }: StatusPillProps) {
  const { t } = useI18n()
  const preset = PRESETS[status] ?? PRESETS.ok
  const tone: PillTone = solid && status === 'critical' ? 'criticalSolid' : preset.tone
  return (
    <Pill tone={tone} icon={withIcon ? preset.icon : undefined} className={className}>
      {children ?? t(preset.label)}
    </Pill>
  )
}
