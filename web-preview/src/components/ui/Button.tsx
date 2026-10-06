import type { ComponentProps } from 'react'
import { Link } from 'react-router-dom'
import type { LucideIcon } from 'lucide-react'
import { cn } from '../../lib/cn'
import { Spinner } from './Spinner'

/**
 * primary = azul ruta (acción por defecto) · accent = ámbar señal (SOLO "Conectar Satrack") ·
 * secondary = papel con borde · light / lightGhost = solo sobre paneles oscuros (HeroPanel) · ghost = terciario.
 */
export type ButtonVariant = 'primary' | 'accent' | 'secondary' | 'light' | 'lightGhost' | 'ghost'

export interface ButtonStyleProps {
  /** @default "primary" */
  variant?: ButtonVariant
  /** "lg" = CTA grande de 18px de radio, 16px de texto. */
  size?: 'lg'
  /** Ancho completo. @default false */
  block?: boolean
  /**
   * Acción destructiva (cancelar un viaje): pinta el texto con `error-text`. Solo tiene efecto con
   * `secondary` y `ghost`; la skill no tiene variante "danger". @default false
   */
  destructive?: boolean
  className?: string
}

const BASE =
  'inline-flex cursor-pointer items-center justify-center gap-2 rounded-control border border-transparent px-4 py-3 min-h-(--tap-min) ' +
  'text-base font-medium leading-[1.2] no-underline outline-hidden transition-all duration-300 ease-out focus-ring ' +
  'disabled:cursor-not-allowed disabled:opacity-60'

const VARIANT: Record<ButtonVariant, string> = {
  primary: 'bg-primary text-on-primary hover:not-disabled:bg-primary-soft hover-lift',
  accent: 'bg-accent text-on-accent hover:not-disabled:bg-accent-dark hover-lift',
  secondary: 'border-line bg-paper text-ink hover-lift',
  light: 'bg-paper text-ink hover:not-disabled:bg-cloud hover-lift',
  lightGhost: 'border-paper/20 bg-paper/8 text-paper hover:not-disabled:bg-paper/14 hover-lift',
  ghost: 'bg-transparent text-mist hover:not-disabled:bg-cloud-soft hover:not-disabled:text-ink',
}

const DESTRUCTIVE: Partial<Record<ButtonVariant, string>> = {
  secondary: 'border-line bg-paper text-error-text hover-lift',
  ghost: 'bg-transparent text-error-text hover:not-disabled:bg-cloud-soft',
}

/**
 * Clases de un botón. Úsala para estilizar otro elemento como botón (p. ej. un `<a>` externo);
 * `Button` y `ButtonLink` la usan por dentro.
 */
export function buttonClasses({ variant = 'primary', size, block = false, destructive = false, className }: ButtonStyleProps = {}): string {
  return cn(
    BASE,
    (destructive && DESTRUCTIVE[variant]) || VARIANT[variant],
    size === 'lg' && 'px-5 py-4 text-body rounded-[18px]',
    block && 'w-full',
    className,
  )
}

interface IconProps {
  /** Icono Lucide antes del texto: 16px (18px con size="lg"). */
  icon?: LucideIcon
  /** Icono Lucide después del texto (p. ej. ArrowRight). */
  iconAfter?: LucideIcon
}

function ButtonContent({ icon: Icon, iconAfter: IconAfter, size, children }: IconProps & Pick<ButtonStyleProps, 'size'> & { children?: ComponentProps<'span'>['children'] }) {
  const px = size === 'lg' ? 18 : 16
  return (
    <>
      {Icon && <Icon size={px} aria-hidden="true" />}
      {children}
      {IconAfter && <IconAfter size={px} aria-hidden="true" />}
    </>
  )
}

export interface ButtonProps extends Omit<ComponentProps<'button'>, 'className'>, ButtonStyleProps, IconProps {
  /** Muestra spinner + "Espera..." y deshabilita el botón. @default false */
  loading?: boolean
}

/**
 * Botón de la marca. `type` es "button" por defecto (no envía formularios por accidente):
 * el botón de envío debe pasar `type="submit"`.
 */
export function Button({
  variant,
  size,
  block,
  destructive,
  loading = false,
  icon,
  iconAfter,
  className,
  type = 'button',
  disabled,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      className={buttonClasses({ variant, size, block, destructive, className })}
      disabled={loading || disabled}
      aria-busy={loading || undefined}
      {...props}
    >
      {loading ? (
        <span className="inline-flex items-center gap-2">
          <Spinner />
          <span>Espera...</span>
        </span>
      ) : (
        <ButtonContent icon={icon} iconAfter={iconAfter} size={size}>
          {children}
        </ButtonContent>
      )}
    </button>
  )
}

export interface ButtonLinkProps extends Omit<ComponentProps<typeof Link>, 'className'>, ButtonStyleProps, IconProps {}

/** Enlace de react-router con la piel de `Button` (misma API visual). Para URLs externas usa `<a className={buttonClasses()}>`. */
export function ButtonLink({ variant, size, block, destructive, icon, iconAfter, className, children, ...props }: ButtonLinkProps) {
  return (
    <Link className={buttonClasses({ variant, size, block, destructive, className })} {...props}>
      <ButtonContent icon={icon} iconAfter={iconAfter} size={size}>
        {children}
      </ButtonContent>
    </Link>
  )
}
