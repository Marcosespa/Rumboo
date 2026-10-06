import type { ComponentProps, ReactNode } from 'react'
import { useI18n } from '../../i18n'
import { cn } from '../../lib/cn'
import { StatusPill } from './StatusPill'

export interface AlertCardProps extends Omit<ComponentProps<'div'>, 'title'> {
  /** attention = cloud-soft · critical = tinte de error. @default "attention" */
  severity?: 'attention' | 'critical'
  title: ReactNode
  detail?: ReactNode
  /** Línea meta en mayúsculas: tipo · fecha · dato. */
  meta?: ReactNode
  /** Muestra la pill de severidad ("Atención" / "Urgente", con icono). @default true */
  pill?: boolean
  /** Botones de acción, en una grilla responsive. */
  actions?: ReactNode
}

/**
 * Tarjeta de aviso o error. Para errores que aparecen de golpe pasa `role="alert"`;
 * para avisos informativos `role="status"`.
 */
export function AlertCard({ severity = 'attention', title, detail, meta, pill = true, actions, className, ...props }: AlertCardProps) {
  const { t } = useI18n()
  const critical = severity === 'critical'
  return (
    <div
      className={cn(
        'rounded-subcard border p-4 transition-all duration-300 ease-out',
        critical ? 'border-error/20 bg-error/8' : 'border-line/70 bg-cloud-soft/70',
        className,
      )}
      {...props}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="m-0 text-base font-semibold text-ink">{title}</p>
          {detail && <p className="m-0 mt-1 text-base leading-relaxed text-mist">{detail}</p>}
          {meta && <p className="m-0 mt-2 text-xs uppercase tracking-[0.16em] text-mist">{meta}</p>}
        </div>
        {pill && (
          <StatusPill status={critical ? 'critical' : 'attention'} solid={critical} withIcon>
            {t(critical ? 'status.severity.critical' : 'status.severity.attention')}
          </StatusPill>
        )}
      </div>
      {actions && <div className="mt-4 grid grid-cols-[repeat(auto-fit,minmax(140px,1fr))] gap-2">{actions}</div>}
    </div>
  )
}
