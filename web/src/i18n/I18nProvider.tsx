import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { formatAgo, formatDate, formatWeightNumber } from './format'
import { LANG_STORAGE_KEY, detectLang, errorText, formatNumber, translate, type Lang, type MessageKey, type TParams } from './translate'

export interface I18n {
  lang: Lang
  /** Cambia el idioma, lo guarda en localStorage (`rumbo.lang`) y actualiza <html lang>. */
  setLang: (lang: Lang) => void
  /** Traduce una clave tipada: t('nav.panel'), t('trips.count', { count: 3 }). */
  t: (key: MessageKey, params?: TParams) => string
  /** Fecha y hora cortas, siempre en America/Bogota. Valor vacío o inválido → "Sin dato" / "No data". */
  formatDate: (value?: string | null) => string
  /** "Hace 5 min" / "5 min ago" desde un instante ISO. */
  formatAgo: (value?: string | null) => string
  /** Peso con unidad: "12.000 kg" / "12,000 kg". */
  formatWeight: (value: number) => string
  /** Número con separadores del idioma. */
  formatNumber: (value: number, options?: Intl.NumberFormatOptions) => string
  /** Texto de un error (ApiError o cualquier otro) listo para mostrar. */
  errorText: (error: unknown) => string
}

function build(lang: Lang, setLang: (lang: Lang) => void): I18n {
  return {
    lang,
    setLang,
    t: (key, params) => translate(lang, key, params),
    formatDate: (value) => formatDate(lang, value),
    formatAgo: (value) => formatAgo(lang, value),
    formatWeight: (value) => `${formatWeightNumber(lang, value)} kg`,
    formatNumber: (value, options) => formatNumber(lang, value, options),
    errorText: (error) => errorText(lang, error),
  }
}

// Sin provider (p. ej. pruebas de un componente suelto) se usa español y setLang no hace nada.
const Context = createContext<I18n>(build('es', () => {}))

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(detectLang)

  const setLang = useCallback((next: Lang) => {
    setLangState(next)
    try {
      localStorage.setItem(LANG_STORAGE_KEY, next)
    } catch {
      /* sin almacenamiento: el idioma vale solo para esta sesión */
    }
  }, [])

  useEffect(() => {
    document.documentElement.lang = lang
    document.title = `Rumbo · ${translate(lang, 'layout.tagline')}`
  }, [lang])

  const value = useMemo(() => build(lang, setLang), [lang, setLang])
  return <Context.Provider value={value}>{children}</Context.Provider>
}

/** Idioma, traductor y formateadores. Úsalo en todo componente que muestre texto. */
export function useI18n(): I18n {
  return useContext(Context)
}
