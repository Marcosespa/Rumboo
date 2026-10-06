/** Une nombres de clase descartando valores vacíos. No resuelve conflictos de Tailwind. */
export function cn(...parts: Array<string | false | null | undefined>): string {
  return parts.filter(Boolean).join(' ')
}
