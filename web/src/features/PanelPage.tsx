import { ChartColumn } from 'lucide-react'
import { EmptyState, PageHeader } from '../components/ui'
import { useI18n } from '../i18n'

export function PanelPage() {
  const { t } = useI18n()
  return (
    <>
      <PageHeader title={t('placeholder.panel.title')} subtitle={t('placeholder.panel.subtitle')} />
      <EmptyState icon={ChartColumn} text={t('placeholder.underConstruction')} />
    </>
  )
}
