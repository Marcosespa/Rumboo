import { useId, type ComponentProps, type ReactNode } from 'react'
import { cn } from '../../lib/cn'

export interface SectionCardProps extends Omit<ComponentProps<'section'>, 'title'> {
  /** Título de la sección (h2, 16px / 600). */
  title?: ReactNode
  /** Una frase que explica qué responde la sección. */
  subtitle?: ReactNode
  /** Acción alineada a la derecha del encabezado (botón ghost o enlace). */
  action?: ReactNode
}

/** Contenedor base de cada sección: papel, borde line, radio 28px, sombra baja. Los ítems internos van en subtarjetas cloud-soft. */
export function SectionCard({ title, subtitle, action, className, children, ...props }: SectionCardProps) {
  const titleId = useId()
  return (
    <section
      aria-labelledby={title ? titleId : undefined}
      className={cn('rounded-card border border-line bg-paper p-5 shadow-card transition-all duration-300 ease-out', className)}
      {...props}
    >
      {(title || subtitle || action) && (
        <div className="mb-4 flex items-start justify-between gap-4">
          <div className="min-w-0">
            {title && (
              <h2 id={titleId} className="m-0 text-body font-semibold tracking-tight text-ink">
                {title}
              </h2>
            )}
            {subtitle && <p className="m-0 mt-1 text-base leading-relaxed text-mist">{subtitle}</p>}
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  )
}
