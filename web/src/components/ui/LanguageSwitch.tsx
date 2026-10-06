import { useI18n, type Lang } from '../../i18n'
import { SegmentedControl } from './SegmentedControl'

export interface LanguageSwitchProps {
  className?: string
}

/** Selector compacto de idioma ES / EN (SegmentedControl). Cambia el idioma de toda la app y lo recuerda. */
export function LanguageSwitch({ className }: LanguageSwitchProps) {
  const { lang, setLang, t } = useI18n()
  return (
    <SegmentedControl
      compact
      aria-label={t('layout.language')}
      value={lang}
      onChange={(value) => setLang(value as Lang)}
      options={[
        { value: 'es', label: 'ES', ariaLabel: t('layout.languageEs') },
        { value: 'en', label: 'EN', ariaLabel: t('layout.languageEn') },
      ]}
      className={className}
    />
  )
}
