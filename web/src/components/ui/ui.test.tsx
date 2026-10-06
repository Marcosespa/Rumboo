import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { Button, ButtonLink, ConfirmDialog, Field, Plate, SatrackStatusPill, StatusPill, TripStatusPill, buttonClasses } from './index'
import { count, plate } from '../../lib/format'
import type { TripState } from '../../api/types'

describe('Field', () => {
  it('shows the error, marks the input invalid and links hint and error', () => {
    render(<Field label="Placa" hint="Ej. WLN 482" error="Revisa la placa" />)
    const input = screen.getByLabelText('Placa')
    expect(screen.getByText('Revisa la placa')).toBeInTheDocument()
    expect(input).toHaveAttribute('aria-invalid', 'true')
    const described = input.getAttribute('aria-describedby') ?? ''
    expect(described).toContain(screen.getByText('Revisa la placa').id)
    expect(described).toContain(screen.getByText('Ej. WLN 482').id)
  })

  it('has no aria-invalid without an error, forwards native props and onChange receives the value', () => {
    const onChange = vi.fn()
    render(<Field label="Usuario" name="usuario" autoComplete="username" required onChange={onChange} />)
    const input = screen.getByLabelText(/Usuario/)
    expect(input).not.toHaveAttribute('aria-invalid')
    expect(input).toHaveAttribute('autocomplete', 'username')
    expect(input).toBeRequired()
    fireEvent.change(input, { target: { value: 'marcos' } })
    expect(onChange).toHaveBeenCalledWith('marcos')
  })
})

describe('status pills', () => {
  it('StatusPill renders its label and an icon when asked', () => {
    const { container } = render(<StatusPill status="critical" withIcon />)
    expect(screen.getByText('Urgente')).toBeInTheDocument()
    expect(container.querySelector('svg')).toBeInTheDocument()
  })

  it.each<[TripState, string]>([
    ['registrado', 'Sin verificar'],
    ['programado', 'Programado'],
    ['en_ruta', 'En ruta'],
    ['entregado', 'Entregado'],
    ['cancelado', 'Cancelado'],
  ])('TripStatusPill %s shows text and icon', (state, label) => {
    const { container } = render(<TripStatusPill state={state} />)
    expect(screen.getByText(label)).toBeInTheDocument()
    expect(container.querySelector('svg')).toBeInTheDocument()
  })

  it('SatrackStatusPill shows text and icon', () => {
    const { container } = render(<SatrackStatusPill estado="credenciales_invalidas" />)
    expect(screen.getByText('Revisa las credenciales')).toBeInTheDocument()
    expect(container.querySelector('svg')).toBeInTheDocument()
  })
})

describe('Button', () => {
  it('loading shows "Espera..." and is disabled', () => {
    render(<Button loading>Guardar viaje</Button>)
    const button = screen.getByRole('button', { name: 'Espera...' })
    expect(button).toBeDisabled()
    expect(screen.queryByText('Guardar viaje')).not.toBeInTheDocument()
  })

  it('does not submit forms by default', () => {
    render(<Button>Agregar remesa</Button>)
    expect(screen.getByRole('button')).toHaveAttribute('type', 'button')
  })

  it('ButtonLink renders a link with the button skin', () => {
    render(
      <MemoryRouter>
        <ButtonLink to="/viajes/nuevo" variant="secondary">
          Nuevo viaje
        </ButtonLink>
      </MemoryRouter>,
    )
    const link = screen.getByRole('link', { name: 'Nuevo viaje' })
    expect(link).toHaveAttribute('href', '/viajes/nuevo')
    expect(link.className).toBe(buttonClasses({ variant: 'secondary' }))
  })
})

describe('ConfirmDialog', () => {
  it('names the dialog and calls the handlers', () => {
    const onConfirm = vi.fn()
    const onCancel = vi.fn()
    render(
      <ConfirmDialog open title="Cancelar viaje" description="Esta acción no se puede deshacer." confirmLabel="Sí, cancelar" onConfirm={onConfirm} onCancel={onCancel} />,
    )
    expect(screen.getByRole('dialog', { name: 'Cancelar viaje' })).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Volver' }))
    expect(onCancel).toHaveBeenCalledTimes(1)
    fireEvent.click(screen.getByRole('button', { name: 'Sí, cancelar' }))
    expect(onConfirm).toHaveBeenCalledTimes(1)
  })
})

describe('plate and count', () => {
  it('formats 6-character plates as "ABC 123"', () => {
    expect(plate('wln482')).toBe('WLN 482')
    expect(plate('WLN-482')).toBe('WLN 482')
    expect(plate(' WLN 482 ')).toBe('WLN 482')
    expect(plate('abc12d')).toBe('ABC 12D')
  })

  it('uppercases other plates without splitting them', () => {
    expect(plate('ab123')).toBe('AB123')
  })

  it('Plate renders the formatted plate', () => {
    render(<Plate value="wln482" />)
    expect(screen.getByText('WLN 482')).toBeInTheDocument()
  })

  it('count picks singular or plural', () => {
    expect(count(1, 'viaje', 'viajes')).toBe('1 viaje')
    expect(count(0, 'viaje', 'viajes')).toBe('0 viajes')
    expect(count(12, 'viaje', 'viajes')).toBe('12 viajes')
  })
})
