import { CheckCircle2, Clock3, TriangleAlert, type LucideIcon } from 'lucide-react'
import { useI18n, type MessageKey } from '../../i18n'
import { Pill, type PillTone } from './Pill'

interface EstadoMeta {
  label: MessageKey
  tone: PillTone
  icon: LucideIcon
}

const ESTADOS: Record<string, EstadoMeta> = {
  ok: { label: 'status.satrack.ok', tone: 'success', icon: CheckCircle2 },
  sin_verificar: { label: 'status.satrack.sin_verificar', tone: 'warning', icon: Clock3 },
  credenciales_invalidas: { label: 'status.satrack.credenciales_invalidas', tone: 'critical', icon: TriangleAlert },
  falla: { label: 'status.satrack.falla', tone: 'critical', icon: TriangleAlert },
}

const UNKNOWN: EstadoMeta = { label: 'status.satrack.unknown', tone: 'neutral', icon: Clock3 }

export interface SatrackStatusPillProps {
  /** `estado` de la cuenta Satrack: ok · sin_verificar · credenciales_invalidas · falla. */
  estado: string
  className?: string
}

/** Pill del estado de la conexión con Satrack: siempre color + icono + texto (traducido). */
export function SatrackStatusPill({ estado, className }: SatrackStatusPillProps) {
  const { t } = useI18n()
  const meta = ESTADOS[estado] ?? UNKNOWN
  return (
    <Pill tone={meta.tone} icon={meta.icon} className={className}>
      {t(meta.label)}
    </Pill>
  )
}
