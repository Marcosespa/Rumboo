import {afterEach, describe, expect, it, vi} from 'vitest'
import {ago, date, weight} from './format'

describe('display formatting', () => {
  afterEach(() => vi.useRealTimers())

  it('shows dates only when the value is valid', () => {
    expect(date(null)).toBe('Sin dato')
    expect(date('not-a-date')).toBe('Sin dato')
    expect(date('2026-01-15T18:00:00Z')).toContain('15')
  })

  it('returns the localized weight without a unit suffix', () => {
    expect(weight(1250.5)).toBe('1.250,5')
    expect(weight(Number.NaN)).toBe('Sin dato')
  })

  it('does not describe invalid or future GPS times as recent', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-10-06T12:00:00Z'))
    expect(ago('not-a-date')).toBe('Hora GPS no disponible')
    expect(ago('2026-10-06T12:01:00Z')).toBe('Hora GPS adelantada')
    expect(ago('2026-10-06T11:58:00Z')).toBe('Hace 2 min')
  })
})
