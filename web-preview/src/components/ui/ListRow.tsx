import type { ComponentProps, ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { cn } from '../../lib/cn'

export interface ListRowProps extends Omit<ComponentProps<'div'>, 'title'> {
  /** Texto principal (se trunca en una línea). */
  title: ReactNode
  /** Línea secundaria en mist. */
  meta?: ReactNode
  /** Valor a la derecha, ya formateado (se muestra con peso 600). */
  amount?: ReactNode
  /** expense = rojo con signo menos · income = azul · neutral = tinta. Solo afecta a `amount`. @default "neutral" */
  tone?: 'expense' | 'income' | 'neutral'
  /** Reemplaza a `amount`: pill, chevron, hora… */
  trailing?: ReactNode
  /** Si se pasa, la fila es un enlace de react-router con hover cloud-soft. */
  to?: string
}

const AMOUNT_COLOR = { expense: 'text-error', income: 'text-primary', neutral: 'text-ink' } as const

/** Fila de lista con divisor fino entre filas. Envuélvelas en un `<ul>` con `<li>` si necesitas semántica de lista. */
export function ListRow({ title, meta, amount, tone = 'neutral', trailing, to, className, ...props }: ListRowProps) {
  const classes = cn('flex items-center justify-between gap-4 border-b border-line/70 py-3 last:border-b-0', to && '-mx-3 rounded-control px-3 text-ink no-underline outline-hidden transition-all duration-300 ease-out hover:bg-cloud-soft focus-ring', className)
  const content = (
    <>
      <div className="min-w-0">
        <p className="m-0 truncate text-base font-semibold text-ink">{title}</p>
        {meta && <p className="m-0 mt-1 text-base text-mist">{meta}</p>}
      </div>
      {trailing ?? (amount !== undefined && (
        <span className={cn('flex-none text-base font-semibold', AMOUNT_COLOR[tone])}>
          {tone === 'expense' ? '-' : ''}
          {amount}
        </span>
      ))}
    </>
  )
  if (to) {
    return (
      <Link to={to} className={classes} {...(props as Omit<ComponentProps<typeof Link>, 'to' | 'className'>)}>
        {content}
      </Link>
    )
  }
  return (
    <div className={classes} {...props}>
      {content}
    </div>
  )
}
