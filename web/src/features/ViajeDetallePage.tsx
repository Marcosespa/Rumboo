import { Truck } from 'lucide-react'
import { EmptyState, PageHeader } from '../components/ui'
import { useI18n } from '../i18n'

export function ViajeDetallePage() {
  const { t } = useI18n()
  return (
    <>
      <PageHeader title={t('placeholder.tripDetail.title')} subtitle={t('placeholder.tripDetail.subtitle')} />
      <EmptyState icon={Truck} text={t('placeholder.underConstruction')} />
    </>
  )
}
