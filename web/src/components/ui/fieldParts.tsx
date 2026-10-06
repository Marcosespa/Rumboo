import { useId, type ReactNode } from 'react'
import { cn } from '../../lib/cn'

/** Piel común de Field / SelectField / TextAreaField (`.r-input` de la skill). */
export const INPUT_CLASSES =
  'box-border w-full rounded-control border border-line bg-cloud-soft px-4 py-3 text-base text-ink outline-hidden ' +
  'transition-all duration-300 ease-out placeholder:text-mist focus:border-primary focus:bg-paper focus:shadow-(--focus-ring) ' +
  'disabled:cursor-not-allowed disabled:opacity-60'

export const INPUT_ERROR_CLASSES = 'border-error'

export interface FieldChromeProps {
  /** Texto del label. Sin label, pasa `aria-label` al control. */
  label?: string
  /** Ayuda corta bajo el control, en mist. */
  hint?: string
  /** Mensaje de error bajo el control (text-error-text). Marca el control con aria-invalid. */
  error?: string
  /** Clases del contenedor (ancho, columnas de grid…). */
  className?: string
  /** Clases extra del control (input / select / textarea). */
  inputClassName?: string
}

/** Ids y atributos ARIA compartidos por los tres campos. */
export function useFieldIds(idProp: string | undefined, hint?: string, error?: string, describedBy?: string) {
  const reactId = useId()
  const id = idProp ?? reactId
  const hintId = hint ? `${id}-hint` : undefined
  const errorId = error ? `${id}-error` : undefined
  return {
    id,
    hintId,
    errorId,
    describedBy: [describedBy, hintId, errorId].filter(Boolean).join(' ') || undefined,
    invalid: error ? true : undefined,
  }
}

interface FieldShellProps {
  id: string
  label?: string
  required?: boolean
  hint?: string
  hintId?: string
  error?: string
  errorId?: string
  className?: string
  children: ReactNode
}

/** Label + control + ayuda + error. */
export function FieldShell({ id, label, required, hint, hintId, error, errorId, className, children }: FieldShellProps) {
  return (
    <div className={cn('block', className)}>
      {label && (
        <label htmlFor={id} className="mb-2 block text-base font-medium text-ink">
          {label}
          {required && (
            <span aria-hidden="true" className="ml-0.5 text-error-text">
              *
            </span>
          )}
        </label>
      )}
      {children}
      {hint && (
        <p id={hintId} className="mt-1.5 text-sm text-mist">
          {hint}
        </p>
      )}
      {error && (
        <p id={errorId} className="mt-1.5 text-sm text-error-text">
          {error}
        </p>
      )}
    </div>
  )
}
