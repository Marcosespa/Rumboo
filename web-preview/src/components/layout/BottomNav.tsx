import { NavLink } from 'react-router-dom'
import { cn } from '../../lib/cn'
import { NAV_ITEMS } from './navItems'

/**
 * Barra inferior flotante (< 860px): píldora fija con safe-area, 5 destinos con la etiqueta
 * siempre visible y el activo relleno en ink. Icono sobre etiqueta hasta 640px para que
 * las cinco etiquetas quepan sin truncarse.
 */
export function BottomNav() {
  return (
    <nav
      aria-label="Navegación móvil"
      className="pointer-events-none fixed inset-x-0 bottom-0 z-30 flex justify-center px-4 pt-4 pb-[calc(env(safe-area-inset-bottom)+14px)] nav:hidden"
    >
      <div className="pointer-events-auto flex w-full max-w-(--content-max) items-center justify-between gap-1 rounded-card border border-line/80 bg-paper/95 px-3 py-2 shadow-nav backdrop-blur-xl">
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              cn(
                'flex min-w-0 flex-1 flex-col items-center justify-center gap-1 rounded-control px-1 py-2 text-sm font-medium no-underline outline-hidden transition-all duration-300 ease-out focus-ring sm:flex-row sm:gap-2 sm:px-3 sm:py-3 sm:text-base',
                isActive ? 'bg-ink text-paper shadow-xs' : 'text-mist hover:bg-cloud-soft hover:text-ink',
              )
            }
          >
            <Icon size={16} aria-hidden="true" />
            <span className="max-w-full truncate">{label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  )
}
