import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import PageLayout from '../components/layout/PageLayout'
import Loader from '../components/ui/Loader'
import { formatCurrency } from '../utils/formatCurrency'
import { formatDate } from '../utils/formatDate'
import { api } from "../services/apiClients"

type ApplicationItem = {
  id: number | string
  status?: string
  amount?: number
  created_at?: string
  product_name?: string
}

function getStatusLabel(status?: string) {
  const labels: Record<string, string> = {
    draft: 'Черновик',
    pending: 'На рассмотрении',
    submitted: 'Отправлена',
    approved: 'Одобрена',
    rejected: 'Отклонена',
    cancelled: 'Отменена',
  }

  return labels[status?.toLowerCase() ?? ''] ?? status ?? 'Не указан'
}

function getStatusClass(status?: string) {
  const normalized = status?.trim().toLowerCase()

  const classes: Record<string, string> = {
    draft: 'status-draft',
    pending: 'status-pending',
    submitted: 'status-submitted',
    approved: 'status-approved',
    rejected: 'status-rejected',
    cancelled: 'status-rejected',
  }

  return classes[normalized ?? ''] ?? 'status-unknown'
}

export default function ApplicationsPage() {
  const [items, setItems] = useState<ApplicationItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    api.get('/applications')
      .then(({ data }) => {
        const list = Array.isArray(data) ? data : data.items ?? data.applications ?? []
        if (active) setItems(list)
      })
      .catch(() => {
        if (active) setError('Не удалось загрузить заявки.')
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  return (
    <PageLayout>
      <div className="page-heading">
        <span className="eyebrow">Кредитование</span>
        <h1>Мои заявки</h1>
        <p>Здесь отображаются созданные вами заявки.</p>
      </div>

      <div className="section-heading">
        <h2>История заявок</h2>
        <Link className="primary-button" to="/applications/new">
          Новая заявка
        </Link>
      </div>

      {loading && <Loader text="Загружаем заявки..." />}
      {error && <div className="notice">{error}</div>}

      {!loading && !error && items.length === 0 && (
        <div className="content-card">
          <h2>Заявок пока нет</h2>
          <p>Создайте первую заявку, чтобы она появилась в этом списке.</p>
          <Link to="/applications/new" className="primary-button">
            Создать заявку
          </Link>
        </div>
      )}

      {!loading && items.length > 0 && (
        <div className="application-list">
          {items.map((item) => (
            <Link
              key={item.id}
              to={`/applications/${item.id}`}
              className="application-row"
            >
              <div>
                <strong>Заявка №{item.id}</strong>
                <p>{item.product_name || 'Кредитный продукт'}</p>
                {item.created_at && <small>{formatDate(item.created_at)}</small>}
              </div>
              <div>
                {item.amount != null && <strong>{formatCurrency(item.amount)}</strong>}
                <span className={`status-pill ${getStatusClass(item.status)}`}>
  {getStatusLabel(item.status)}
</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </PageLayout>
  )
}