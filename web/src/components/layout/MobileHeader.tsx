import { LogOut } from 'lucide-react'
import { useI18n } from '../../i18n'
import { IconButton } from '../ui/IconButton'
import { LanguageSwitch } from '../ui/LanguageSwitch'
import { BrandChip } from './BrandChip'

export interface MobileHeaderProps {
  companyName?: string
  onLogout: () => void
  loggingOut?: boolean
}

/** Header fijo de móvil (< 860px): marca, nombre de la transportadora, idioma y salir. */
export function MobileHeader({ companyName, onLogout, loggingOut = false }: MobileHeaderProps) {
  const { t } = useI18n()
  return (
    <header className="sticky top-0 z-20 flex items-center gap-3 border-b border-line/80 bg-paper/90 px-(--page-pad-x) py-3 backdrop-blur-xl nav:hidden">
      <BrandChip />
      <p className="m-0 min-w-0 flex-1 truncate text-base text-mist">{companyName}</p>
      <LanguageSwitch />
      <IconButton icon={LogOut} label={t('layout.logout')} onClick={onLogout} disabled={loggingOut} />
    </header>
  )
}
