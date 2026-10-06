export const TOKEN_KEY = 'rumboo.session'
export const DEMO_KEY = 'rumboo.demo.session'
export function isDemoSession() { return sessionStorage.getItem(DEMO_KEY) === 'active' }
export type FieldError = {campo: string; mensaje: string}
export class ApiError extends Error {
  constructor(public status: number, message: string, public errores: FieldError[] = []) {super(message)}
}
export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  if (import.meta.env.DEV && isDemoSession()) {
    try {
      const {handleDemoApi} = await import('../demo/api')
      return await handleDemoApi<T>(path, options)
    } catch (error) {
      if (error instanceof Error && 'status' in error && typeof error.status === 'number') {
        const demoError = error as Error & {status: number; errores?: FieldError[]}
        throw new ApiError(demoError.status, demoError.message, demoError.errores || [])
      }
      throw error
    }
  }
  const token = sessionStorage.getItem(TOKEN_KEY)
  let response: Response
  try {
    response = await fetch(`/api${path}`, {...options, headers: {'Content-Type': 'application/json', ...(token ? {Authorization: `Bearer ${token}`} : {}), ...options.headers}})
  } catch {throw new ApiError(0, 'No pudimos conectar. Revisa tu conexión y vuelve a intentar.')}
  const result = await response.json().catch(() => ({}))
  if (!response.ok) {
    if (response.status === 401 && path !== '/auth/login') {
      sessionStorage.removeItem(TOKEN_KEY)
      window.dispatchEvent(new Event('rumboo:unauthorized'))
    }
    throw new ApiError(response.status, typeof result.detail === 'string' ? result.detail : 'No fue posible completar la operación', result.errores || [])
  }
  return result as T
}
export const post = <T,>(path: string, data?: unknown) => api<T>(path, {method: 'POST', body: data === undefined ? undefined : JSON.stringify(data)})
