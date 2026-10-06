import { Truck } from 'lucide-react'
import { EmptyState, PageHeader } from '../components/ui'

export function FlotaPage() {
  return (
    <>
      <PageHeader title="Flota" subtitle="Aquí verás dónde están tus vehículos." />
      <EmptyState icon={Truck} text="Pantalla en construcción." />
    </>
  )
}
