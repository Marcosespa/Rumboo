import type { ReactNode } from 'react'
import { cn } from '../../lib/cn'

export interface BrandChipProps {
  /** Ruta del cóndor. @default "/brand/condor-sm.png" */
  logoSrc?: string
  /** Wordmark visible. @default "Rumbo" */
  children?: ReactNode
  className?: string
}

/** Pastilla con el cóndor y el wordmark "Rumbo". El logo siempre acompaña al wordmark. */
export function BrandChip({ logoSrc = '/brand/condor-sm.png', children = 'Rumbo', className }: BrandChipProps) {
  return (
    <span className={cn('inline-flex items-center gap-2 rounded-pill border border-line bg-cloud-soft py-1 pr-3 pl-1.5 text-sm font-semibold tracking-wide text-primary', className)}>
      <img src={logoSrc} alt="Logo de Rumbo: cóndor andino" className="size-6 object-contain" />
      {children}
    </span>
  )
}
