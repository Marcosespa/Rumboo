import { cn } from '../../lib/cn'

export interface SkeletonProps {
  /** Tamaño y forma con utilidades de Tailwind, p. ej. "h-16 w-full rounded-subcard". @default "h-4 w-full rounded-chip" */
  className?: string
}

/** Esqueleto de carga: fondo cloud-soft con brillo suave. Es decorativo (aria-hidden); anuncia la carga en el contenedor con role="status". */
export function Skeleton({ className = 'h-4 w-full rounded-chip' }: SkeletonProps) {
  return <div aria-hidden="true" className={cn('shimmer', className)} />
}
