import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { ApiError, api, DEMO_KEY, isDemoSession, post, TOKEN_KEY } from '../api/client'
import type { User } from '../api/types'
type Auth = {user: User | null; loading: boolean; error: string; isDemo: boolean; retry: () => void; login: (usuario: string, password: string) => Promise<void>; startDemo: () => Promise<void>; logout: () => Promise<void>}
const Context = createContext<Auth | null>(null)
export function AuthProvider({children}: {children: ReactNode}) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [demoActive, setDemoActive] = useState(() => import.meta.env.DEV && isDemoSession())
  const [attempt, setAttempt] = useState(0)
  const queryClient = useQueryClient()
  useEffect(() => {
    let alive = true
    const unauthorized = () => {setUser(null); queryClient.clear()}
    window.addEventListener('rumboo:unauthorized', unauthorized)
    if (import.meta.env.DEV && isDemoSession()) {
      setLoading(true); setError('')
      api<User>('/auth/me').then(value => {if (alive) {setUser(value); setDemoActive(true)}}).catch(() => {
        if (alive) {setUser(null); setDemoActive(false); sessionStorage.removeItem(DEMO_KEY)}
      }).finally(() => {if (alive) setLoading(false)})
    } else if (sessionStorage.getItem(TOKEN_KEY)) {
      setLoading(true); setError('')
      api<User>('/auth/me').then(value => {if (alive) setUser(value)}).catch(err => {
        if (alive && (!(err instanceof ApiError) || err.status !== 401)) setError('No pudimos comprobar tu sesión. Vuelve a intentar.')
      }).finally(() => {if (alive) setLoading(false)})
    } else setLoading(false)
    return () => {alive = false; window.removeEventListener('rumboo:unauthorized', unauthorized)}
  }, [queryClient, attempt])
  const login = async (usuario: string, password: string) => {
    const result = await post<{token: string; usuario: User}>('/auth/login', {usuario, password})
    queryClient.clear(); sessionStorage.removeItem(DEMO_KEY); setDemoActive(false); sessionStorage.setItem(TOKEN_KEY, result.token); setUser(result.usuario); setError('')
  }
  const startDemo = async () => {
    if (!import.meta.env.DEV) throw new Error('La vista de ejemplo solo está disponible durante el desarrollo.')
    queryClient.clear(); sessionStorage.removeItem(TOKEN_KEY)
    const {clearDemoData} = await import('../demo/api')
    clearDemoData()
    sessionStorage.setItem(DEMO_KEY, 'active')
    setLoading(true); setError('')
    try {
      const demoUser = await api<User>('/auth/me')
      setUser(demoUser); setDemoActive(true)
    } catch (err) {
      sessionStorage.removeItem(DEMO_KEY); clearDemoData(); setDemoActive(false); setUser(null)
      throw err
    } finally {setLoading(false)}
  }
  const logout = async () => {
    if (import.meta.env.DEV && isDemoSession()) {
      sessionStorage.removeItem(DEMO_KEY); sessionStorage.removeItem(TOKEN_KEY)
      const {clearDemoData} = await import('../demo/api')
      clearDemoData(); setUser(null); setDemoActive(false); setError(''); queryClient.clear()
      return
    }
    await post('/auth/logout')
    sessionStorage.removeItem(TOKEN_KEY); sessionStorage.removeItem(DEMO_KEY); setDemoActive(false); setUser(null); queryClient.clear()
  }
  return <Context.Provider value={{user, loading, error, isDemo: demoActive, retry: () => setAttempt(v => v + 1), login, startDemo, logout}}>{children}</Context.Provider>
}
export function useAuth() {const context = useContext(Context); if (!context) throw new Error('AuthProvider requerido'); return context}
