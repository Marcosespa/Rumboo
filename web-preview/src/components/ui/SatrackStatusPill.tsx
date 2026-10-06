import { CheckCircle2, Clock3, TriangleAlert, type LucideIcon } from 'lucide-react'
import { Pill, type PillTone } from './Pill'

interface EstadoMeta {
  label: string
  tone: PillTone
  icon: LucideIcon
}

const ESTADOS: Record<string, EstadoMeta> = {
  ok: { label: 'Conectado', tone: 'success', icon: CheckCircle2 },
  sin_verificar: { label: 'Por verificar', tone: 'warning', icon: Clock3 },
  credenciales_invalidas: { label: 'Revisa las credenciales', tone: 'critical', icon: TriangleAlert },
  falla: { label: 'Conexión con fallas', tone: 'critical', icon: TriangleAlert },
}

const UNKNOWN: EstadoMeta = { label: 'Por revisar', tone: 'neutral', icon: Clock3 }

export interface SatrackStatusPillProps {
  /** `estado` de la cuenta Satrack: ok · sin_verificar · credenciales_invalidas · falla. */
  estado: string
  className?: string
}

/** Pill del estado de la conexión con Satrack: siempre color + icono + texto. */
export function SatrackStatusPill({ estado, className }: SatrackStatusPillProps) {
  const meta = ESTADOS[estado] ?? UNKNOWN
  return (
    <Pill tone={meta.tone} icon={meta.icon} className={className}>
      {meta.label}
    </Pill>
  )
}
