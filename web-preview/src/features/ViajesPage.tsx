import { ClipboardList } from 'lucide-react'
import { EmptyState, PageHeader } from '../components/ui'

export function ViajesPage() {
  return (
    <>
      <PageHeader title="Viajes" subtitle="Aquí verás tus viajes y en qué van." />
      <EmptyState icon={ClipboardList} text="Pantalla en construcción." />
    </>
  )
}
