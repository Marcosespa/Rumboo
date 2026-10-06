import type { ReactNode } from 'react'
import { cn } from '../../lib/cn'
import { Overline } from './Overline'

export interface PageHeaderProps {
  /** Etiqueta superior en mayúsculas (escríbela en sentence case: "Tu operación, al día"). */
  overline?: ReactNode
  /** Título de la pantalla: el h1 de la página (28px). */
  title: ReactNode
  /** Una frase que explica qué responde la pantalla. */
  subtitle?: ReactNode
  /** Acciones a la derecha (botones); bajan debajo del título en pantallas angostas. */
  action?: ReactNode
  className?: string
}

/** Encabezado de página: overline + h1 28px + subtítulo mist + acciones. Va al inicio de cada pantalla. */
export function PageHeader({ overline, title, subtitle, action, className }: PageHeaderProps) {
  return (
    <header className={cn('flex flex-wrap items-start justify-between gap-4', className)}>
      <div className="min-w-0">
        {overline && <Overline>{overline}</Overline>}
        <h1 className={cn('m-0 text-h1 font-semibold leading-tight text-ink', overline ? 'mt-2' : undefined)}>{title}</h1>
        {subtitle && <p className="m-0 mt-1 max-w-xl text-base leading-relaxed text-mist">{subtitle}</p>}
      </div>
      {action && <div className="flex flex-wrap items-center gap-2">{action}</div>}
    </header>
  )
}
