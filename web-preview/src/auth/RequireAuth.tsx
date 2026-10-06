import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext'
import { AlertCard, Button, Spinner } from '../components/ui'

/** Ruta de layout: muestra <Outlet/> solo con sesión; si no, envía a /login conservando la ruta pedida. */
export function RequireAuth() {
  const auth = useAuth()
  const location = useLocation()

  if (auth.loading) {
    return (
      <main className="grid min-h-dvh place-items-center bg-paper px-(--page-pad-x)">
        <div role="status" className="flex items-center gap-3 text-base text-mist">
          <Spinner size="md" />
          Cargando tu operación…
        </div>
      </main>
    )
  }

  if (auth.error) {
    return (
      <main className="grid min-h-dvh place-items-center bg-paper px-(--page-pad-x)">
        <AlertCard
          severity="critical"
          role="alert"
          pill={false}
          title={auth.error}
          actions={<Button onClick={auth.retry}>Reintentar</Button>}
          className="w-full max-w-(--content-narrow)"
        />
      </main>
    )
  }

  return auth.user ? <Outlet /> : <Navigate to="/login" state={{ from: location.pathname + location.search }} replace />
}
