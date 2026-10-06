import { LogIn } from 'lucide-react'
import { BrandChip } from '../components/layout'
import { EmptyState, LanguageSwitch, PageHeader } from '../components/ui'
import { useI18n } from '../i18n'

export function LoginPage() {
  const { t } = useI18n()
  return (
    <main className="mx-auto flex min-h-dvh w-full max-w-(--content-narrow) flex-col justify-center gap-6 px-(--page-pad-x)">
      <div className="flex items-center justify-between gap-3">
        <BrandChip />
        <LanguageSwitch />
      </div>
      <PageHeader title={t('placeholder.login.title')} subtitle={t('layout.tagline')} />
      <EmptyState icon={LogIn} text={t('placeholder.underConstruction')} />
    </main>
  )
}
