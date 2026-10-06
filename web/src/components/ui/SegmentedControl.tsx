import { useRef, type KeyboardEvent } from 'react'
import { cn } from '../../lib/cn'

export type SegmentedOption = string | { value: string; label: string; /** Nombre accesible si la etiqueta visible es una sigla ('ES'). */ ariaLabel?: string }

export interface SegmentedControlProps {
  /** Strings o pares { value, label }. */
  options: SegmentedOption[]
  value?: string
  /** Recibe el nuevo valor. */
  onChange?: (value: string) => void
  /** Estira los segmentos al ancho de la fila. @default false */
  block?: boolean
  /** Versión compacta (px-3 py-2, 13px) para barras y encabezados. @default false */
  compact?: boolean
  /** Nombre accesible del grupo (recomendado). */
  'aria-label'?: string
  className?: string
}

/**
 * Selector segmentado: pista cloud-soft, segmento activo en ink con texto paper.
 * role="tablist" con navegación por flechas, Inicio y Fin.
 */
export function SegmentedControl({ options, value, onChange, block = false, compact = false, className, ...props }: SegmentedControlProps) {
  const items = options.map((o) => (typeof o === 'string' ? { value: o, label: o } : o))
  const refs = useRef<Array<HTMLButtonElement | null>>([])
  const activeIndex = Math.max(0, items.findIndex((o) => o.value === value))

  const onKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    const last = items.length - 1
    const next =
      event.key === 'ArrowRight' ? (activeIndex + 1) % items.length
      : event.key === 'ArrowLeft' ? (activeIndex - 1 + items.length) % items.length
      : event.key === 'Home' ? 0
      : event.key === 'End' ? last
      : -1
    if (next < 0 || !items.length) return
    event.preventDefault()
    refs.current[next]?.focus()
    onChange?.(items[next].value)
  }

  return (
    <div
      role="tablist"
      aria-label={props['aria-label']}
      onKeyDown={onKeyDown}
      className={cn('gap-1 rounded-control border border-line bg-cloud-soft p-1', block ? 'flex w-full' : 'inline-flex', className)}
    >
      {items.map((item, index) => {
        const active = item.value === value
        return (
          <button
            key={item.value}
            ref={(node) => {
              refs.current[index] = node
            }}
            type="button"
            role="tab"
            aria-selected={active}
            aria-label={'ariaLabel' in item ? item.ariaLabel : undefined}
            tabIndex={index === activeIndex ? 0 : -1}
            onClick={onChange ? () => onChange(item.value) : undefined}
            className={cn(
              'cursor-pointer rounded-chip border-0 font-medium outline-hidden transition-all duration-300 ease-out focus-ring',
              compact ? 'px-3 py-2 text-sm' : 'px-4 py-2 text-base',
              block && 'flex-1',
              active ? 'bg-ink text-paper shadow-xs' : 'bg-transparent text-mist hover:text-ink',
            )}
          >
            {item.label}
          </button>
        )
      })}
    </div>
  )
}
