import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from './auth/AuthContext'
import { RequireAuth } from './auth/RequireAuth'
import { AppShell } from './components/layout'
import { NotFoundPage } from './features/NotFoundPage'
import { LoginPage } from './features/LoginPage'
import { PanelPage } from './features/PanelPage'
import { ViajesPage } from './features/ViajesPage'
import { NuevoViajePage } from './features/NuevoViajePage'
import { ViajeDetallePage } from './features/ViajeDetallePage'
import { FlotaPage } from './features/FlotaPage'
import { AjustesPage } from './features/AjustesPage'
import '@fontsource/inter/400.css'
import '@fontsource/inter/500.css'
import '@fontsource/inter/600.css'
import '@fontsource/inter/700.css'
import '@fontsource/inter-tight/500.css'
import '@fontsource/inter-tight/600.css'
import '@fontsource/inter-tight/700.css'
import 'leaflet/dist/leaflet.css'
import './index.css'

const client = new QueryClient({defaultOptions: {queries: {retry: 1, staleTime: 10000, refetchOnWindowFocus: false}}})
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={client}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route element={<RequireAuth />}>
              <Route element={<AppShell />}>
                <Route index element={<PanelPage />} />
                <Route path="viajes" element={<ViajesPage />} />
                <Route path="viajes/nuevo" element={<NuevoViajePage />} />
                <Route path="viajes/:id" element={<ViajeDetallePage />} />
                <Route path="flota" element={<FlotaPage />} />
                <Route path="ajustes" element={<AjustesPage />} />
                <Route path="*" element={<NotFoundPage />} />
              </Route>
            </Route>
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
)
