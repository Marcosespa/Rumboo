export const date = (value?: string | null) => value ? new Intl.DateTimeFormat('es-CO', {dateStyle: 'medium', timeStyle: 'short', timeZone: 'America/Bogota'}).format(new Date(value)) : 'Sin dato'
export const weight = (value: number) => `${new Intl.NumberFormat('es-CO', {maximumFractionDigits: 1}).format(value)} kg`
export function ago(value?: string | null) {
  if (!value) return 'Hora GPS no disponible'
  const minutes = Math.max(0, Math.floor((Date.now() - new Date(value).getTime()) / 60000))
  return minutes < 1 ? 'Hace un momento' : minutes < 60 ? `Hace ${minutes} min` : `Hace ${Math.floor(minutes / 60)} h`
}
export const localDateToISO = (value: string) => `${value}:00-05:00`

/** Placa en mayúsculas; las de 6 caracteres se parten como "ABC 123" ("abc123" → "ABC 123"). */
export function plate(value: string): string {
  const upper = value.trim().toUpperCase()
  const compact = upper.replace(/[\s-]+/g, '')
  return /^[A-Z0-9]{6}$/.test(compact) ? `${compact.slice(0, 3)} ${compact.slice(3)}` : upper
}

/** Cantidad con su unidad en singular o plural: count(1, 'viaje', 'viajes') → "1 viaje". */
export const count = (n: number, singular: string, plural: string) =>
  `${new Intl.NumberFormat('es-CO').format(n)} ${n === 1 ? singular : plural}`
