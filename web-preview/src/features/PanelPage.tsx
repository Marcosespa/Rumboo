import { ChartColumn } from 'lucide-react'
import { EmptyState, PageHeader } from '../components/ui'

export function PanelPage() {
  return (
    <>
      <PageHeader title="Panel" subtitle="Aquí verás cómo va tu operación ahora." />
      <EmptyState icon={ChartColumn} text="Pantalla en construcción." />
    </>
  )
}
