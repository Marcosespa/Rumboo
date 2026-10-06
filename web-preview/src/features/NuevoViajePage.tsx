import { PlusCircle } from 'lucide-react'
import { EmptyState, PageHeader } from '../components/ui'

export function NuevoViajePage() {
  return (
    <>
      <PageHeader title="Nuevo viaje" subtitle="Aquí registrarás un viaje nuevo." />
      <EmptyState icon={PlusCircle} text="Pantalla en construcción." />
    </>
  )
}
