import type { ComponentProps } from 'react'
import { cn } from '../../lib/cn'
import { FieldShell, INPUT_CLASSES, INPUT_ERROR_CLASSES, useFieldIds, type FieldChromeProps } from './fieldParts'

export interface FieldProps extends FieldChromeProps, Omit<ComponentProps<'input'>, 'onChange' | 'className' | 'value' | 'defaultValue'> {
  value?: string
  /** Recibe el nuevo VALOR (no el evento). */
  onChange?: (value: string) => void
}

/**
 * Campo de texto con label. Relleno cloud-soft que pasa a paper con anillo azul al enfocar.
 * Reenvía todas las props nativas del input (name, type, autoComplete, required, maxLength, inputMode…).
 * Con `error` el campo queda `aria-invalid` y enlazado al mensaje con `aria-describedby`.
 */
export function Field({ label, hint, error, className, inputClassName, onChange, id: idProp, required, ...props }: FieldProps) {
  const ids = useFieldIds(idProp, hint, error, props['aria-describedby'])
  return (
    <FieldShell {...ids} label={label} required={required} hint={hint} error={error} className={className}>
      <input
        {...props}
        id={ids.id}
        required={required}
        aria-invalid={ids.invalid ?? props['aria-invalid']}
        aria-describedby={ids.describedBy}
        className={cn(INPUT_CLASSES, error && INPUT_ERROR_CLASSES, inputClassName)}
        onChange={onChange ? (event) => onChange(event.target.value) : undefined}
      />
    </FieldShell>
  )
}
