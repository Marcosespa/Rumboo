import { ClipboardList } from 'lucide-react'
import { EmptyState, PageHeader } from '../components/ui'
import { useI18n } from '../i18n'

export function ViajesPage() {
  const { t } = useI18n()
  return (
    <>
      <PageHeader title={t('placeholder.trips.title')} subtitle={t('placeholder.trips.subtitle')} />
      <EmptyState icon={ClipboardList} text={t('placeholder.underConstruction')} />
    </>
  )
}
