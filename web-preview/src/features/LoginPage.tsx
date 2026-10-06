import { LogIn } from 'lucide-react'
import { BrandChip } from '../components/layout'
import { EmptyState, PageHeader } from '../components/ui'

export function LoginPage() {
  return (
    <main className="mx-auto flex min-h-dvh w-full max-w-(--content-narrow) flex-col justify-center gap-6 px-(--page-pad-x)">
      <BrandChip className="self-start" />
      <PageHeader title="Entra a tu operación" subtitle="Tu operación, al día." />
      <EmptyState icon={LogIn} text="Pantalla en construcción." />
    </main>
  )
}
