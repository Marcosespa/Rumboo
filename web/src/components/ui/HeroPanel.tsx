import type { ComponentProps, ReactNode } from 'react'
import { cn } from '../../lib/cn'
import { Metric } from './Metric'
import { Overline } from './Overline'

export interface HeroPanelProps extends Omit<ComponentProps<'section'>, 'children'> {
  /** Etiqueta superior; el componente la pone en mayúsculas (escríbela en sentence case). */
  overline?: ReactNode
  /** Cifra protagonista a 38px, p. ej. "12" o "12 viajes". */
  figure?: ReactNode
  /** Una línea que explica la cifra. */
  caption?: ReactNode
  /** ink (Panel) o primary azul. @default "ink" */
  tone?: 'ink' | 'primary'
  /** Hasta 4, como tiles translúcidos (con 4, en móvil se acomodan en 2 columnas). */
  metrics?: Array<{ label: ReactNode; value: ReactNode }>
  /** Botones `light` / `lightGhost` (solo esas variantes sobre fondo oscuro). */
  actions?: ReactNode
  children?: ReactNode
}

const COLUMNS: Record<number, string> = {
  1: 'grid-cols-1',
  2: 'grid-cols-2',
  3: 'grid-cols-3',
  4: 'grid-cols-2 sm:grid-cols-4',
}

/** Panel héroe oscuro en la parte alta de cada pantalla: la respuesta a "la pregunta" de la pantalla. */
export function HeroPanel({ overline, figure, caption, tone = 'ink', metrics = [], actions, children, className, ...props }: HeroPanelProps) {
  const shown = metrics.slice(0, 4)
  return (
    <section className={cn('rounded-panel px-5 py-6 text-paper shadow-hero', tone === 'primary' ? 'bg-primary' : 'bg-ink', className)} {...props}>
      {overline && <Overline tone="onDark">{overline}</Overline>}
      {figure && <h2 className="m-0 mt-3 text-figure font-semibold tracking-tight">{figure}</h2>}
      {caption && <p className="m-0 mt-2 max-w-xs text-base leading-relaxed opacity-70">{caption}</p>}
      {shown.length > 0 && (
        <div className={cn('mt-6 grid gap-3', COLUMNS[shown.length])}>
          {shown.map((metric, index) => (
            <Metric key={index} label={metric.label} value={metric.value} />
          ))}
        </div>
      )}
      {actions && <div className="mt-6 grid grid-cols-[repeat(auto-fit,minmax(180px,1fr))] gap-3">{actions}</div>}
      {children}
    </section>
  )
}
