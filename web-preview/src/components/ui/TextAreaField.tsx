import type { ComponentProps } from 'react'
import { cn } from '../../lib/cn'
import { FieldShell, INPUT_CLASSES, INPUT_ERROR_CLASSES, useFieldIds, type FieldChromeProps } from './fieldParts'

export interface TextAreaFieldProps extends FieldChromeProps, Omit<ComponentProps<'textarea'>, 'onChange' | 'className' | 'value' | 'defaultValue'> {
  /** @default 3 */
  rows?: number
  value?: string
  /** Recibe el nuevo VALOR (no el evento). */
  onChange?: (value: string) => void
}

/** Textarea con label y la misma piel que `Field` (incluye `error`, `hint` y `required`). */
export function TextAreaField({ label, hint, error, className, inputClassName, rows = 3, onChange, id: idProp, required, ...props }: TextAreaFieldProps) {
  const ids = useFieldIds(idProp, hint, error, props['aria-describedby'])
  return (
    <FieldShell {...ids} label={label} required={required} hint={hint} error={error} className={className}>
      <textarea
        {...props}
        id={ids.id}
        rows={rows}
        required={required}
        aria-invalid={ids.invalid ?? props['aria-invalid']}
        aria-describedby={ids.describedBy}
        className={cn(INPUT_CLASSES, 'resize-y leading-relaxed', error && INPUT_ERROR_CLASSES, inputClassName)}
        onChange={onChange ? (event) => onChange(event.target.value) : undefined}
      />
    </FieldShell>
  )
}
