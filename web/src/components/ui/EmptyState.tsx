import type { ReactNode } from 'react'
import { Inbox, type LucideIcon } from 'lucide-react'
import { cn } from '../../lib/cn'

export interface EmptyStateProps {
  /** Icono Lucide dentro de la caja de 44px. @default Inbox */
  icon?: LucideIcon
  /** Texto amable que SIEMPRE sugiere la siguiente acción, p. ej. "Aún no tienes viajes. Registra el primero para empezar a monitorearlo." */
  text: ReactNode
  /** Botón o enlace de la siguiente acción, debajo del texto. */
  action?: ReactNode
  className?: string
}

/** Estado vacío: subtarjeta con borde punteado, caja de icono y texto guía. */
export function EmptyState({ icon: Icon = Inbox, text, action, className }: EmptyStateProps) {
  return (
    <div
      className={cn(
        'rounded-subcard border border-dashed border-line bg-cloud-soft/70 px-4 py-6 text-center transition-all duration-300 ease-out',
        className,
      )}
    >
      <div className="mx-auto flex size-11 items-center justify-center rounded-control bg-paper text-mist shadow-xs">
        <Icon size={16} aria-hidden="true" />
      </div>
      <p className="m-0 mt-3 text-base leading-relaxed text-mist">{text}</p>
      {action && <div className="mt-4 flex justify-center">{action}</div>}
    </div>
  )
}
