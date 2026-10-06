import { PlusCircle } from 'lucide-react'
import { EmptyState, PageHeader } from '../components/ui'
import { useI18n } from '../i18n'

export function NuevoViajePage() {
  const { t } = useI18n()
  return (
    <>
      <PageHeader title={t('placeholder.newTrip.title')} subtitle={t('placeholder.newTrip.subtitle')} />
      <EmptyState icon={PlusCircle} text={t('placeholder.underConstruction')} />
    </>
  )
}
