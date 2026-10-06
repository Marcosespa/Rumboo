import { LOCALES, TIME_ZONE, formatNumber, translate, type Lang } from './translate'

function parse(value?: string | null): Date | null {
  if (!value) return null
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? null : parsed
}

/** Fecha y hora cortas en hora de Colombia: "15 ene 2026, 1:00 p. m." / "Jan 15, 2026, 1:00 PM". */
export function formatDate(lang: Lang, value?: string | null): string {
  const parsed = parse(value)
  if (!parsed) return translate(lang, 'common.noData')
  return new Intl.DateTimeFormat(LOCALES[lang], { dateStyle: 'medium', timeStyle: 'short', timeZone: TIME_ZONE }).format(parsed)
}

/** Peso en kg, solo el número ("12.000" / "12,000"). Añade la unidad en la interfaz. */
export function formatWeightNumber(lang: Lang, value: number): string {
  return Number.isFinite(value) ? formatNumber(lang, value, { maximumFractionDigits: 1 }) : translate(lang, 'common.noData')
}

/** Tiempo transcurrido desde un reporte GPS: "Hace 5 min" / "5 min ago". */
export function formatAgo(lang: Lang, value?: string | null, now: number = Date.now()): string {
  const parsed = parse(value)
  if (!parsed) return translate(lang, 'common.time.unavailable')
  const diff = now - parsed.getTime()
  if (diff < -30_000) return translate(lang, 'common.time.ahead')
  const minutes = Math.max(0, Math.floor(diff / 60_000))
  if (minutes < 1) return translate(lang, 'common.time.justNow')
  if (minutes < 60) return translate(lang, 'common.time.minutes', { count: minutes })
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return translate(lang, 'common.time.hours', { count: hours })
  return translate(lang, 'common.time.days', { count: Math.floor(hours / 24) })
}
