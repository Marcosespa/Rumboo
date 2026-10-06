import type { ComponentProps } from 'react'
import type { LucideIcon } from 'lucide-react'
import { cn } from '../../lib/cn'

export interface IconButtonProps extends Omit<ComponentProps<'button'>, 'children' | 'aria-label' | 'title'> {
  /** Icono Lucide, p. ej. `LogOut`, `RefreshCw`. */
  icon: LucideIcon
  /** Etiqueta accesible obligatoria (control solo de icono): es el aria-label y el tooltip. */
  label: string
  /** Tamaño del icono en px. @default 16 */
  size?: number
}

/** Botón cuadrado de 44px con borde para acciones de utilidad (actualizar, cerrar sesión). */
export function IconButton({ icon: Icon, label, size = 16, className, type = 'button', ...props }: IconButtonProps) {
  return (
    <button
      type={type}
      aria-label={label}
      title={label}
      className={cn(
        'inline-flex size-(--tap-min) flex-none cursor-pointer items-center justify-center rounded-control border border-line bg-paper text-ink shadow-xs',
        'outline-hidden transition-all duration-300 ease-out hover-lift focus-ring disabled:cursor-not-allowed disabled:opacity-60',
        className,
      )}
      {...props}
    >
      <Icon size={size} aria-hidden="true" />
    </button>
  )
}
