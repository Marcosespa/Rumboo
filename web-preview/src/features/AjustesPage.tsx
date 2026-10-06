import { Settings } from 'lucide-react'
import { EmptyState, PageHeader } from '../components/ui'

export function AjustesPage() {
  return (
    <>
      <PageHeader title="Ajustes" subtitle="Aquí revisarás la conexión con Satrack." />
      <EmptyState icon={Settings} text="Pantalla en construcción." />
    </>
  )
}
