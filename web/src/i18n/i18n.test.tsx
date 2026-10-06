import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'
import { ApiError } from '../api/client'
import { LanguageSwitch, TripStatusPill } from '../components/ui'
import { ago, date, weight } from '../lib/format'
import { I18nProvider, LANG_STORAGE_KEY, detectLang, en, es, translate, useI18n } from './index'

function keys(node: unknown, prefix = ''): string[] {
  if (!node || typeof node !== 'object') return [prefix]
  const entries = Object.entries(node)
  return entries.length ? entries.flatMap(([k, v]) => keys(v, prefix ? `${prefix}.${k}` : k)) : [prefix]
}

function Probe() {
  const { t, formatWeight, lang, errorText } = useI18n()
  return (
    <p>
      {lang}|{t('common.time.days', { count: 1 })}|{t('common.time.days', { count: 3 })}|{formatWeight(12000)}|{errorText(new ApiError(0, 'network'))}
    </p>
  )
}

beforeEach(() => {
  localStorage.clear()
  document.documentElement.lang = ''
})

describe('dictionaries', () => {
  it('es and en have identical key sets', () => {
    expect(keys(en).sort()).toEqual(keys(es).sort())
  })

  it('no value is empty', () => {
    for (const dict of [es, en]) {
      const flat = (n: unknown): string[] => (typeof n === 'string' ? [n] : n && typeof n === 'object' ? Object.values(n).flatMap(flat) : [])
      expect(flat(dict).every((s) => s.trim().length > 0)).toBe(true)
    }
  })

  it('keeps the brand wordmark untranslated and the tagline in both languages', () => {
    expect(translate('es', 'layout.tagline')).toBe('Tu operación, al día')
    expect(translate('en', 'layout.tagline')).toBe('Your operation, up to date')
    expect(translate('en', 'layout.brandAlt')).toContain('Rumbo')
  })
})

describe('translate', () => {
  it('interpolates and picks plural forms', () => {
    expect(translate('es', 'common.time.days', { count: 1 })).toBe('Hace 1 día')
    expect(translate('es', 'common.time.days', { count: 3 })).toBe('Hace 3 días')
    expect(translate('en', 'common.time.days', { count: 1 })).toBe('1 day ago')
    expect(translate('en', 'common.time.hours', { count: 2 })).toBe('2 h ago')
  })

  it('falls back to the key when it does not exist', () => {
    expect(translate('en', 'no.such.key' as never)).toBe('no.such.key')
  })
})

describe('formatters', () => {
  it('delegate by language and always use Bogota time', () => {
    // 2026-01-15T03:00Z es 14 de enero a las 10:00 p. m. en Bogotá
    expect(date('2026-01-15T03:00:00Z')).toContain('14')
    expect(date('2026-01-15T03:00:00Z', 'en')).toMatch(/Jan 14, 2026/)
    expect(date(null, 'en')).toBe('No data')
    expect(weight(1250.5)).toBe('1.250,5')
    expect(weight(1250.5, 'en')).toBe('1,250.5')
    expect(ago('not-a-date', 'en')).toBe('GPS time not available')
  })
})

describe('I18nProvider', () => {
  it('starts from localStorage, persists changes and sets <html lang>', () => {
    localStorage.setItem(LANG_STORAGE_KEY, 'es')
    render(
      <I18nProvider>
        <LanguageSwitch />
        <TripStatusPill state="en_ruta" />
      </I18nProvider>,
    )
    expect(screen.getByText('En ruta')).toBeInTheDocument()
    expect(document.documentElement.lang).toBe('es')
    expect(screen.getByRole('tablist', { name: 'Idioma' })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('tab', { name: 'English' }))
    expect(screen.getByText('On route')).toBeInTheDocument()
    expect(screen.queryByText('En ruta')).not.toBeInTheDocument()
    expect(screen.getByRole('tablist', { name: 'Language' })).toBeInTheDocument()
    expect(document.documentElement.lang).toBe('en')
    expect(localStorage.getItem(LANG_STORAGE_KEY)).toBe('en')
  })

  it('detects English browsers when nothing is stored', () => {
    expect(detectLang()).toBe('en') // jsdom: navigator.language = en-US
    localStorage.setItem(LANG_STORAGE_KEY, 'es')
    expect(detectLang()).toBe('es')
  })

  it('exposes formatters, plurals and error texts', () => {
    localStorage.setItem(LANG_STORAGE_KEY, 'en')
    render(
      <I18nProvider>
        <Probe />
      </I18nProvider>,
    )
    expect(screen.getByText("en|1 day ago|3 days ago|12,000 kg|We couldn't connect. Check your connection and try again.")).toBeInTheDocument()
  })
})
