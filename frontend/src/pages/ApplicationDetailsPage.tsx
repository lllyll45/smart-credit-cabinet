import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import PageLayout from '../components/layout/PageLayout'
import Loader from '../components/ui/Loader'
import Button from '../components/ui/Button'
import { formatCurrency } from '../utils/formatCurrency'
import { api } from '../services/apiClients'

type ApplicationDetails = {
  id: number
  user_id?: number
  credit_product_id?: number
  amount?: string | number | null
  comment?: string | null
  created_at?: string | null
  decision_comment?: string | null
  employment?: string | null
  monthly_income?: string | number | null
  monthly_payment?: string | number | null
  overpayment?: string | number | null
  purpose?: string | null
  status?: string | null
  term_months?: number | null
  total_payment?: string | number | null
  updated_at?: string | null
}

function formatMoney(value?: string | number | null) {
  if (value === null || value === undefined || value === '') {
    return 'Не указано'
  }

  return formatCurrency(Number(value))
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


function formatEmployment(value?: string | null) {
  if (!value) return 'Не указано'

  const labels: Record<string, string> = {
    employed: 'Работа по найму',
    self_employed: 'Самозанятый',
    entrepreneur: 'Предприниматель',
    unemployed: 'Безработный',
    student: 'Студент',
    retired: 'Пенсионер',
  }

  return labels[value.toLowerCase()] ?? value
}

function formatDateTime(value?: string | null) {
  if (!value) return 'Не указано'

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) return value

  return new Intl.DateTimeFormat('ru-RU', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

export default function ApplicationDetailsPage() {
  const { id } = useParams()
  const [item, setItem] = useState<ApplicationDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function loadApplication() {
    const { data } = await api.get<ApplicationDetails>(
      `/applications/${id}`,
    )
    setItem(data)
  }

  useEffect(() => {
    let active = true

    api.get<ApplicationDetails>(`/applications/${id}`)
      .then(({ data }) => {
        if (active) setItem(data)
      })
      .catch(() => {
        if (active) setError('Не удалось загрузить заявку.')
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [id])

  async function submitApplication() {
    setSubmitting(true)
    setError('')

    try {
      await api.post(`/applications/${id}/submit`)
      await loadApplication()
    } catch {
      setError('Не удалось отправить заявку. Проверьте поддержку этого действия на сервере.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <PageLayout>
      <p className="application-back-link">
        <Link to="/applications">← Все заявки</Link>
      </p>

      {loading && <Loader />}
      {error && <div className="notice">{error}</div>}

      {!loading && !error && !item && (
        <div className="content-card">
          <h2>Заявка не найдена</h2>
          <Link to="/applications">Вернуться к списку заявок</Link>
        </div>
      )}

      {item && (
        <>
          <div className="application-detail-heading">
            <div className="page-heading">
              <span className="eyebrow">Кредитная заявка №{item.id}</span>
              <h1>Заявка №{item.id}</h1>
              <p>Информация о заявке, её параметрах и решении по ней.</p>
            </div>

            <span className={`status-pill ${getStatusClass(item.status)}`}>
              {getStatusLabel(item.status)}
            </span>
          </div>

          <section className="content-card application-details-card">
            <h2>Параметры кредита</h2>

            <div className="details-list">
              <div>
                <span>Сумма кредита</span>
                <strong>{formatMoney(item.amount)}</strong>
              </div>
              <div>
                <span>Срок кредита</span>
                <strong>
                  {item.term_months != null
                    ? `${item.term_months} мес.`
                    : 'Не указано'}
                </strong>
              </div>
              <div>
                <span>Цель кредита</span>
                <strong>{item.purpose || 'Не указана'}</strong>
              </div>
            </div>
          </section>

          <section className="content-card application-details-card">
            <h2>Финансовая информация</h2>

            <div className="details-list">
              <div>
                <span>Ежемесячный доход</span>
                <strong>{formatMoney(item.monthly_income)}</strong>
              </div>
              <div>
                <span>Ежемесячный платёж</span>
                <strong>{formatMoney(item.monthly_payment)}</strong>
              </div>
              <div>
                <span>Общая сумма выплат</span>
                <strong>{formatMoney(item.total_payment)}</strong>
              </div>
              <div>
                <span>Переплата</span>
                <strong>{formatMoney(item.overpayment)}</strong>
              </div>
              <div>
                <span>Тип занятости</span>
                <strong>{formatEmployment(item.employment)}</strong>
              </div>
            </div>
          </section>

          <section className="content-card application-details-card">
            <h2>Решение по заявке</h2>

            <div className="details-list">
              <div>
                <span>Статус</span>
                <strong>
                  <span className={`status-pill ${getStatusClass(item.status)}`}>
                    {getStatusLabel(item.status)}
                  </span>
                </strong>
              </div>
            </div>

            <div className="application-note">
              <strong>Комментарий по решению</strong>
              <p>
                {item.decision_comment || 'Комментарий по решению отсутствует.'}
              </p>
            </div>

            <div className="application-note">
              <strong>Комментарий пользователя</strong>
              <p>{item.comment || 'Комментарий не добавлен.'}</p>
            </div>
          </section>

          <section className="content-card application-details-card">
            <h2>Сведения о заявке</h2>

            <div className="details-list">
              <div>
                <span>Дата создания</span>
                <strong>{formatDateTime(item.created_at)}</strong>
              </div>
              <div>
                <span>Последнее изменение</span>
                <strong>{formatDateTime(item.updated_at)}</strong>
              </div>
            </div>
          </section>

          {item.status?.trim().toLowerCase() === 'draft' && (
            <div className="application-actions">
              <Button onClick={submitApplication} disabled={submitting}>
                {submitting ? 'Отправляем...' : 'Отправить заявку'}
              </Button>
            </div>
          )}
        </>
      )}
    </PageLayout>
  )
}