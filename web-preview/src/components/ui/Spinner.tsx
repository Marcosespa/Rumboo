import { cn } from '../../lib/cn'

export interface SpinnerProps {
  /** sm = 16px (botones, como en la skill) · md = 24px (pantallas de carga). @default "sm" */
  size?: 'sm' | 'md'
  className?: string
}

/** Anillo giratorio decorativo (aria-hidden). Quien lo usa solo debe anunciar el estado ("Cargando…"). */
export function Spinner({ size = 'sm', className }: SpinnerProps) {
  return (
    <span
      aria-hidden="true"
      className={cn(
        'inline-block flex-none animate-spin rounded-full border-2 border-current border-r-transparent',
        size === 'md' ? 'size-6' : 'size-4',
        className,
      )}
    />
  )
}
