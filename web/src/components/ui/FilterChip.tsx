import type { ComponentProps } from 'react'
import { cn } from '../../lib/cn'

export interface FilterChipProps extends Omit<ComponentProps<'button'>, 'className'> {
  /** Chip seleccionado: relleno ink con texto paper. Se anuncia con aria-pressed. @default false */
  active?: boolean
  className?: string
}

/** Chip redondo de filtro (alternancia). */
export function FilterChip({ active = false, className, type = 'button', ...props }: FilterChipProps) {
  return (
    <button
      type={type}
      aria-pressed={active}
      className={cn(
        'inline-flex cursor-pointer items-center gap-1.5 rounded-pill border px-3 py-2 text-sm font-medium outline-hidden transition-all duration-300 ease-out focus-ring',
        active ? 'border-ink bg-ink text-paper shadow-xs' : 'border-line bg-paper text-mist hover:text-ink',
        className,
      )}
      {...props}
    />
  )
}
