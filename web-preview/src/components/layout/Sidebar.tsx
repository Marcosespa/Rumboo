import { NavLink } from 'react-router-dom'
import { LogOut } from 'lucide-react'
import { cn } from '../../lib/cn'
import { IconButton } from '../ui/IconButton'
import { Overline } from '../ui/Overline'
import { BrandChip } from './BrandChip'
import { NAV_ITEMS } from './navItems'

export interface SidebarProps {
  userName?: string
  companyName?: string
  onLogout: () => void
  loggingOut?: boolean
}

/** Barra lateral de escritorio (≥ 860px): marca, navegación vertical y bloque de usuario. */
export function Sidebar({ userName, companyName, onLogout, loggingOut = false }: SidebarProps) {
  return (
    <aside className="fixed inset-y-0 left-0 z-20 hidden w-(--sidebar-width) flex-col gap-6 border-r border-line bg-paper px-4 py-6 nav:flex">
      <div className="px-2">
        <BrandChip />
        <Overline className="mt-3">Control de tráfico</Overline>
      </div>
      <nav aria-label="Navegación principal" className="flex flex-1 flex-col gap-1">
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-2 rounded-control px-3 py-3 text-base font-medium no-underline outline-hidden transition-all duration-300 ease-out focus-ring',
                isActive ? 'bg-ink text-paper shadow-xs' : 'text-mist hover:bg-cloud-soft hover:text-ink',
              )
            }
          >
            <Icon size={16} aria-hidden="true" />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="flex items-center gap-3 rounded-subcard border border-line/70 bg-cloud-soft/70 p-3">
        <div className="min-w-0 flex-1">
          <p className="m-0 truncate text-base font-semibold text-ink">{userName}</p>
          <p className="m-0 truncate text-sm text-mist">{companyName}</p>
        </div>
        <IconButton icon={LogOut} label="Cerrar sesión" onClick={onLogout} disabled={loggingOut} />
      </div>
    </aside>
  )
}
