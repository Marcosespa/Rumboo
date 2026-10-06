import { LogOut } from 'lucide-react'
import { IconButton } from '../ui/IconButton'
import { BrandChip } from './BrandChip'

export interface MobileHeaderProps {
  companyName?: string
  onLogout: () => void
  loggingOut?: boolean
}

/** Header fijo de móvil (< 860px): marca, nombre de la transportadora y salir. */
export function MobileHeader({ companyName, onLogout, loggingOut = false }: MobileHeaderProps) {
  return (
    <header className="sticky top-0 z-20 flex items-center gap-3 border-b border-line/80 bg-paper/90 px-(--page-pad-x) py-3 backdrop-blur-xl nav:hidden">
      <BrandChip />
      <p className="m-0 min-w-0 flex-1 truncate text-base text-mist">{companyName}</p>
      <IconButton icon={LogOut} label="Cerrar sesión" onClick={onLogout} disabled={loggingOut} />
    </header>
  )
}
