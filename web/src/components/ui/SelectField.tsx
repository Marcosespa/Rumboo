import type { ComponentProps } from 'react'
import { cn } from '../../lib/cn'
import { FieldShell, INPUT_CLASSES, INPUT_ERROR_CLASSES, useFieldIds, type FieldChromeProps } from './fieldParts'

export type SelectOption = string | { value: string; label: string; disabled?: boolean }

export interface SelectFieldProps extends FieldChromeProps, Omit<ComponentProps<'select'>, 'onChange' | 'className' | 'value' | 'defaultValue' | 'children'> {
  /** Strings o pares { value, label }. Para un "Selecciona…" incluye `{ value: '', label: 'Selecciona…' }`. */
  options: SelectOption[]
  value?: string
  /** Recibe el nuevo VALOR (no el evento). */
  onChange?: (value: string) => void
}

/** Select con label y la misma piel que `Field` (incluye `error`, `hint` y `required`). */
export function SelectField({ label, hint, error, className, inputClassName, options, onChange, id: idProp, required, ...props }: SelectFieldProps) {
  const ids = useFieldIds(idProp, hint, error, props['aria-describedby'])
  return (
    <FieldShell {...ids} label={label} required={required} hint={hint} error={error} className={className}>
      <select
        {...props}
        id={ids.id}
        required={required}
        aria-invalid={ids.invalid ?? props['aria-invalid']}
        aria-describedby={ids.describedBy}
        className={cn(INPUT_CLASSES, error && INPUT_ERROR_CLASSES, inputClassName)}
        onChange={onChange ? (event) => onChange(event.target.value) : undefined}
      >
        {options.map((option) => {
          const o = typeof option === 'string' ? { value: option, label: option, disabled: false } : option
          return (
            <option key={o.value} value={o.value} disabled={o.disabled}>
              {o.label}
            </option>
          )
        })}
      </select>
    </FieldShell>
  )
}
