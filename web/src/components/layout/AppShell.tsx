import { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../../auth/AuthContext'
import { AlertCard } from '../ui/AlertCard'
import { BottomNav } from './BottomNav'
import { MobileHeader } from './MobileHeader'
import { Sidebar } from './Sidebar'

/**
 * Estructura de la bandeja. Desktop-first: desde 860px barra lateral fija de 248px y contenido
 * de hasta 1240px centrado; debajo, header sticky arriba + barra inferior flotante.
 *
 * Las páginas se renderizan en <Outlet/> dentro de una columna con `gap` de 16px: devuelve
 * un fragmento (o tus secciones directamente) y empieza con `PageHeader`. No añadas
 * tu propio `max-w`, gutter ni padding inferior: el shell ya los pone.
 */
export function AppShell() {
  const { user, logout } = useAuth()
  const { pathname } = useLocation()
  const [loggingOut, setLoggingOut] = useState(false)
  const [logoutError, setLogoutError] = useState(false)

  const onLogout = async () => {
    setLoggingOut(true)
    setLogoutError(false)
    try {
      await logout()
    } catch {
      setLogoutError(true)
      setLoggingOut(false)
    }
  }

  return (
    <div className="min-h-dvh bg-paper">
      <a
        href="#contenido"
        className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50 focus:rounded-control focus:bg-ink focus:px-4 focus:py-3 focus:text-base focus:text-paper"
      >
        Saltar al contenido
      </a>
      <Sidebar userName={user?.nombre} companyName={user?.transportadora.nombre} onLogout={onLogout} loggingOut={loggingOut} />
      <div className="nav:pl-(--sidebar-width)">
        <MobileHeader companyName={user?.transportadora.nombre} onLogout={onLogout} loggingOut={loggingOut} />
        <main
          id="contenido"
          tabIndex={-1}
          className="mx-auto w-full max-w-(--content-max) px-(--page-pad-x) pt-6 pb-[calc(env(safe-area-inset-bottom)+7rem)] outline-hidden nav:px-(--page-pad-x-lg) nav:pt-8 nav:pb-8"
        >
          <div key={pathname} className="flex animate-slide-up flex-col gap-(--stack-gap)">
            {logoutError && <AlertCard severity="critical" role="alert" pill={false} title="No pudimos cerrar la sesión. Vuelve a intentar." />}
            <Outlet />
          </div>
        </main>
      </div>
      <BottomNav />
    </div>
  )
}
