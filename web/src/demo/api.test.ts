import {beforeEach, describe, expect, it} from 'vitest'
import {clearDemoData, DemoApiError, handleDemoApi, hasDemoData} from './api'
import type {TripInput} from '../api/types'

beforeEach(() => clearDemoData())

describe('development preview API', () => {
  it('filters and paginates seeded trips using the API query contract', async () => {
    const page = await handleDemoApi<{items: {estado: string; vehiculo: {placa: string}}[]; total: number; page: number; page_size: number}>('/viajes?estado=en_ruta&q=JKL&page=1')
    expect(page).toMatchObject({total: 1, page: 1, page_size: 20})
    expect(page.items[0]).toMatchObject({estado: 'en_ruta', vehiculo: {placa: 'JKL123'}})
  })

  it('creates a registered trip and totals its remesa weights', async () => {
    const input: TripInput = {
      manifiesto: 'MC-NEW-2026', origen: 'Bogotá', destino: 'Pereira',
      salida_estimada: '2026-10-07T10:00:00-05:00', llegada_estimada: '2026-10-07T16:00:00-05:00',
      conductor: {nombre: 'Elena Ruiz', cedula: '12345678', telefono: '3001234567', autoriza_contacto: true},
      vehiculo: {placa: 'GHI890', propietario: 'Transportes del camino'},
      remesas: [{numero: 'R-NEW-1', cliente: 'Comercial La Ruta', peso_kg: 1250.5, cantidad: 12}, {numero: 'R-NEW-2', cliente: 'Mercado Central', peso_kg: 300, cantidad: null}],
    }
    const created = await handleDemoApi<{id: number; estado: string; peso_salida_kg: number; remesas: {peso_kg: number}[]}>('/viajes', {method: 'POST', body: JSON.stringify(input)})
    expect(created).toMatchObject({id: 6, estado: 'registrado', peso_salida_kg: 1550.5})
    expect(created.remesas).toHaveLength(2)
    expect(hasDemoData()).toBe(true)
  })

  it('requires a cancellation reason and records allowed transitions', async () => {
    await expect(handleDemoApi('/viajes/2/transiciones', {method: 'POST', body: JSON.stringify({estado: 'cancelado'})})).rejects.toMatchObject({status: 422})
    const changed = await handleDemoApi<{estado: string; eventos: {detalle: Record<string, unknown>}[]}>('/viajes/2/transiciones', {method: 'POST', body: JSON.stringify({estado: 'en_ruta'})})
    expect(changed.estado).toBe('en_ruta')
    await expect(handleDemoApi('/viajes/2/transiciones', {method: 'POST', body: JSON.stringify({estado: 'entregado'})})).resolves.toMatchObject({estado: 'entregado'})
    await expect(handleDemoApi('/viajes/2/transiciones', {method: 'POST', body: JSON.stringify({estado: 'cancelado'})})).rejects.toMatchObject({status: 409})
  })

  it('does not save Satrack passwords in the preview data', async () => {
    await handleDemoApi('/cuenta-satelital', {method: 'PUT', body: JSON.stringify({usuario: 'cuenta-demo', password: 'esta-no-se-guarda'})})
    expect(sessionStorage.getItem('rumboo.demo.data')).not.toContain('esta-no-se-guarda')
    await expect(handleDemoApi('/viajes/500/transiciones', {method: 'POST', body: JSON.stringify({estado: 'en_ruta'})})).rejects.toBeInstanceOf(DemoApiError)
  })
})
