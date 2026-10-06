import { formatAgo, formatDate, formatWeightNumber } from '../i18n/format'
import type { Lang } from '../i18n/translate'

/*
 * Formateadores puros (fuera de React). En componentes usa los del hook `useI18n()`
 * (`formatDate`, `formatAgo`, `formatWeight`, `formatNumber`), que ya conocen el idioma activo.
 * Las fechas son siempre hora de Colombia (America/Bogota).
 */

/** Fecha y hora cortas; vacío o inválido → "Sin dato" / "No data". */
export const date = (value?: string | null, lang: Lang = 'es') => formatDate(lang, value)
/** Peso como número ("1.250,5"), sin unidad; NaN → "Sin dato". Para "kg" incluido usa `useI18n().formatWeight`. */
export const weight = (value: number, lang: Lang = 'es') => formatWeightNumber(lang, value)
/** "Hace 5 min" / "5 min ago". Hora inválida → "Hora GPS no disponible"; futura → "Hora GPS adelantada". */
export const ago = (value?: string | null, lang: Lang = 'es') => formatAgo(lang, value)
export const localDateToISO = (value: string) => `${value}:00-05:00`

/** Placa en mayúsculas; las de 6 caracteres se parten como "ABC 123" ("abc123" → "ABC 123"). */
export function plate(value: string): string {
  const upper = value.trim().toUpperCase()
  const compact = upper.replace(/[\s-]+/g, '')
  return /^[A-Z0-9]{6}$/.test(compact) ? `${compact.slice(0, 3)} ${compact.slice(3)}` : upper
}

/** @deprecated Solo español. Usa un plural del diccionario: `t('trips.count', { count })`. */
export const count = (n: number, singular: string, plural: string) =>
  `${new Intl.NumberFormat('es-CO').format(n)} ${n === 1 ? singular : plural}`
