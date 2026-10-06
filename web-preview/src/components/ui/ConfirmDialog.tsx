import { useEffect, useId, useRef, type ReactNode, type SyntheticEvent } from 'react'
import { Button } from './Button'

export interface ConfirmDialogProps {
  /** Controlado: true abre el diálogo (modal nativo), false lo cierra. */
  open: boolean
  title: string
  /** Texto breve que explica qué pasará. */
  description?: ReactNode
  /** Contenido extra (p. ej. un `TextAreaField` para el motivo de cancelación). */
  children?: ReactNode
  /** Verbo + objeto: "Iniciar ruta", "Marcar entregado", "Cancelar viaje". */
  confirmLabel: string
  /** @default "Volver" */
  cancelLabel?: string
  /** Pinta la confirmación con texto de error (secondary destructivo), p. ej. cancelar un viaje. @default false */
  destructive?: boolean
  /** Muestra "Espera..." en la confirmación y bloquea cerrar mientras se envía. @default false */
  loading?: boolean
  /** Deshabilita la confirmación (p. ej. motivo vacío). @default false */
  confirmDisabled?: boolean
  onConfirm: () => void
  /** Se llama al pulsar el botón de cancelar, Escape o el fondo. Debe poner `open` en false. */
  onCancel: () => void
}

/**
 * Diálogo de confirmación accesible sobre `<dialog>` nativo: foco atrapado, Escape cierra,
 * el foco vuelve al botón que lo abrió y el scroll de la página queda bloqueado.
 * El foco inicial cae en el primer control (el campo de `children` si existe; si no, "Volver").
 */
export function ConfirmDialog({
  open,
  title,
  description,
  children,
  confirmLabel,
  cancelLabel = 'Volver',
  destructive = false,
  loading = false,
  confirmDisabled = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const ref = useRef<HTMLDialogElement>(null)
  const titleId = useId()
  const descriptionId = useId()

  useEffect(() => {
    const dialog = ref.current
    if (!dialog) return
    if (open && !dialog.open) {
      // jsdom no implementa showModal; en navegadores reales siempre existe.
      if (typeof dialog.showModal === 'function') dialog.showModal()
      else dialog.setAttribute('open', '')
    } else if (!open && dialog.open) {
      if (typeof dialog.close === 'function') dialog.close()
      else dialog.removeAttribute('open')
    }
  }, [open])

  const handleCancel = (event: SyntheticEvent) => {
    // Escape: lo gobierna el estado del padre, no el navegador.
    event.preventDefault()
    if (!loading) onCancel()
  }

  return (
    <dialog
      ref={ref}
      aria-labelledby={titleId}
      aria-describedby={description ? descriptionId : undefined}
      onCancel={handleCancel}
      onClose={() => {
        if (open) onCancel()
      }}
      onClick={(event) => {
        // Clic en el fondo (el propio <dialog>, no su contenido).
        if (event.target === event.currentTarget && !loading) onCancel()
      }}
      className="m-auto w-[calc(100%-2.5rem)] max-w-md animate-slide-up rounded-card border border-line bg-paper p-0 text-ink shadow-panel backdrop:bg-ink/40"
    >
      <div className="p-6">
        <h2 id={titleId} className="m-0 text-h2 font-semibold leading-snug text-ink">
          {title}
        </h2>
        {description && (
          <p id={descriptionId} className="m-0 mt-2 text-base leading-relaxed text-mist">
            {description}
          </p>
        )}
        {children && <div className="mt-4">{children}</div>}
        <div className="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Button variant="secondary" onClick={onCancel} disabled={loading}>
            {cancelLabel}
          </Button>
          <Button
            variant={destructive ? 'secondary' : 'primary'}
            destructive={destructive}
            onClick={onConfirm}
            loading={loading}
            disabled={confirmDisabled}
          >
            {confirmLabel}
          </Button>
        </div>
      </div>
    </dialog>
  )
}
