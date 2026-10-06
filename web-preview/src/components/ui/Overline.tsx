import type { ComponentProps } from 'react'
import { cn } from '../../lib/cn'

export interface OverlineProps extends ComponentProps<'p'> {
  /**
   * mist = sobre papel · primary = énfasis azul · onDark = hereda el color de un panel
   * oscuro con opacidad .6 (HeroPanel). @default "mist"
   */
  tone?: 'mist' | 'primary' | 'onDark'
}

const TONE = {
  mist: 'text-mist',
  primary: 'text-primary',
  onDark: 'opacity-60',
} as const

/** Etiqueta superior: 11px / 600 / MAYÚSCULAS con tracking .2em. Único lugar (con las placas) donde va en mayúsculas. */
export function Overline({ tone = 'mist', className, ...props }: OverlineProps) {
  return (
    <p
      className={cn('m-0 text-xs font-semibold uppercase tracking-overline', TONE[tone], className)}
      {...props}
    />
  )
}
