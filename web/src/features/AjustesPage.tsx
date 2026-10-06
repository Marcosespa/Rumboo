import { Settings } from 'lucide-react'
import { EmptyState, PageHeader } from '../components/ui'
import { useI18n } from '../i18n'

export function AjustesPage() {
  const { t } = useI18n()
  return (
    <>
      <PageHeader title={t('placeholder.settings.title')} subtitle={t('placeholder.settings.subtitle')} />
      <EmptyState icon={Settings} text={t('placeholder.underConstruction')} />
    </>
  )
}
