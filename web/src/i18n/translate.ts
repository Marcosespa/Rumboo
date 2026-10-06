import { en } from './en'
import { es, type Messages } from './es'

export type Lang = 'es' | 'en'
export const LANGS: readonly Lang[] = ['es', 'en']
export const LANG_STORAGE_KEY = 'rumbo.lang'

/** Locale de Intl por idioma. */
export const LOCALES: Record<Lang, string> = { es: 'es-CO', en: 'en-US' }
/** Las fechas SIEMPRE se muestran en hora de Colombia, sin importar el idioma ni el navegador. */
export const TIME_ZONE = 'America/Bogota'

export const MESSAGES: Record<Lang, Messages> = { es, en }

interface PluralForms {
  one: string
  other: string
}

type Paths<T, P extends string = ''> = {
  [K in keyof T & string]: T[K] extends string ? `${P}${K}` : T[K] extends PluralForms ? `${P}${K}` : Paths<T[K], `${P}${K}.`>
}[keyof T & string]

/** Clave de traducción válida con notación de puntos, p. ej. 'nav.panel' o 'common.time.days' (plural). */
export type MessageKey = Paths<Messages>
export type TParams = Record<string, string | number>

function lookup(messages: unknown, key: string): unknown {
  return key.split('.').reduce<unknown>((node, part) => (node && typeof node === 'object' ? (node as Record<string, unknown>)[part] : undefined), messages)
}

export function formatNumber(lang: Lang, value: number, options?: Intl.NumberFormatOptions): string {
  return new Intl.NumberFormat(LOCALES[lang], options).format(value)
}

/**
 * Traduce `key` (fuera de React). Si falta en `lang` cae al español y, si tampoco existe, devuelve la clave.
 * Reemplaza `{nombre}` con `params.nombre`; si el valor es un plural ({ one, other }) elige la forma
 * según `params.count` y le da formato numérico del idioma.
 */
export function translate(lang: Lang, key: MessageKey, params?: TParams): string {
  let value = lookup(MESSAGES[lang], key)
  if (value === undefined) value = lookup(es, key)
  if (value && typeof value === 'object') {
    const count = Number(params?.count ?? 0)
    const form = new Intl.PluralRules(LOCALES[lang]).select(count) === 'one' ? 'one' : 'other'
    value = (value as Record<string, unknown>)[form]
  }
  if (typeof value !== 'string') return key
  return value.replace(/\{(\w+)\}/g, (match, name: string) => {
    const param = params?.[name]
    if (param === undefined) return match
    return name === 'count' && typeof param === 'number' ? formatNumber(lang, param) : String(param)
  })
}

/**
 * Texto de un error para mostrar al usuario. `ApiError.code` 'network' / 'unknown' / 'demo_unavailable' /
 * 'session_check' se traducen con `errors.*`; cualquier otro `detail` del backend se muestra tal como llegó
 * (el servidor responde en español).
 */
export function errorText(lang: Lang, error: unknown): string {
  const code = (error as { code?: unknown } | null)?.code
  if (code === 'network') return translate(lang, 'errors.network')
  if (code === 'demo_unavailable') return translate(lang, 'errors.demoUnavailable')
  if (code === 'session_check') return translate(lang, 'auth.sessionError')
  if (code === 'unknown') return translate(lang, 'errors.unknown')
  if (error instanceof Error && error.message) return error.message
  return translate(lang, 'errors.unknown')
}

/** Idioma inicial: localStorage `rumbo.lang` → navegador en inglés → español. */
export function detectLang(): Lang {
  try {
    const stored = localStorage.getItem(LANG_STORAGE_KEY)
    if (stored === 'es' || stored === 'en') return stored
  } catch {
    /* localStorage no disponible (modo privado, bloqueado): se sigue con el navegador */
  }
  return typeof navigator !== 'undefined' && navigator.language?.toLowerCase().startsWith('en') ? 'en' : 'es'
}
