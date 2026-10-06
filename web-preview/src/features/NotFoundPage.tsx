import { ButtonLink, PageHeader } from '../components/ui'

export function NotFoundPage() {
  return (
    <PageHeader
      title="No encontramos esta página"
      subtitle="Puede que el enlace esté mal escrito o que la página ya no exista."
      action={<ButtonLink to="/">Volver al panel</ButtonLink>}
    />
  )
}
