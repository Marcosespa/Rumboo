import { Truck } from 'lucide-react'
import { EmptyState, PageHeader } from '../components/ui'

export function ViajeDetallePage() {
  return (
    <>
      <PageHeader title="Detalle del viaje" subtitle="Aquí verás dónde va este camión." />
      <EmptyState icon={Truck} text="Pantalla en construcción." />
    </>
  )
}
