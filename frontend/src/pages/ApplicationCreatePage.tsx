import { useNavigate, useSearchParams } from 'react-router-dom'
import PageLayout from '../components/layout/PageLayout'
import ApplicationForm, {
  type ApplicationFormValues,
} from '../features/applications/ApplicationForm'
import { api } from '../services/apiClients'

export default function ApplicationCreatePage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const productIdParam = Number(searchParams.get('productId'))
  const productId =
    Number.isInteger(productIdParam) && productIdParam > 0
      ? productIdParam
      : undefined

  async function handleSubmit(values: ApplicationFormValues) {
    await api.post('/applications', values)
    navigate('/applications', { replace: true })
  }

  return (
    <PageLayout>
      <div className="page-heading">
        <span className="eyebrow">Кредитование</span>
        <h1>Создание заявки</h1>
        <p>Укажите продукт, желаемую сумму и срок кредитования.</p>
      </div>

      <ApplicationForm productId={productId} onSubmit={handleSubmit} />
    </PageLayout>
  )
}