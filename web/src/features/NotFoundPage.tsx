import { ButtonLink, PageHeader } from '../components/ui'
import { useI18n } from '../i18n'

export function NotFoundPage() {
  const { t } = useI18n()
  return <PageHeader title={t('errors.notFound.title')} subtitle={t('errors.notFound.text')} action={<ButtonLink to="/">{t('errors.notFound.action')}</ButtonLink>} />
}
