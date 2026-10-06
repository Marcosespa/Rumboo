import { Truck } from 'lucide-react'
import { EmptyState, PageHeader } from '../components/ui'
import { useI18n } from '../i18n'

export function FlotaPage() {
  const { t } = useI18n()
  return (
    <>
      <PageHeader title={t('placeholder.fleet.title')} subtitle={t('placeholder.fleet.subtitle')} />
      <EmptyState icon={Truck} text={t('placeholder.underConstruction')} />
    </>
  )
}
