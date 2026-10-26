import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import PageLayout from '../components/layout/PageLayout'
import Loader from '../components/ui/Loader'
import Button from '../components/ui/Button'
import { formatCurrency } from '../utils/formatCurrency'
import { api } from '../services/apiClients'
import {
  statusClass,
  statusLabel,
} from '../features/applications/statuses'
import type {
  Application,
  ApplicationHistoryEntry,
} from '../types/comon'

function formatMoney(value?: string | number | null) {
  if (value === null || value === undefined || value === '') {
    return 'Не указано'
  }
  return formatCurrency(Number(value))
}

function formatLegalForm(value?: string | null) {
  if (!value) return 'Не указано'

  const normalized = value.trim().toLowerCase()

  const labels: Record<string, string> = {
    ip: 'ИП',
    individual_entrepreneur: 'ИП',
    'индивидуальный предприниматель': 'ИП',
    ооо: 'ООО',
    llc: 'ООО',
    ao: 'АО',
    пао: 'ПАО',
    зао: 'ЗАО',
    self_employed: 'Самозанятый',
    самозанятый: 'Самозанятый',
  }

  return labels[normalized] ?? value
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
  const [item, setItem] = useState<Application | null>(null)
  const [history, setHistory] = useState<ApplicationHistoryEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function loadAll() {
    if (!id) return

    const { data } = await api.get<Application>(`/applications/${id}`)
    setItem(data)

    try {
      const hist = await api.get<ApplicationHistoryEntry[]>(
        `/applications/${id}/history`,
      )
      setHistory(Array.isArray(hist.data) ? hist.data : [])
    } catch {
      setHistory([])
    }
  }

  useEffect(() => {
    let active = true

    async function load() {
      if (!id) {
        setLoading(false)
        return
      }

      try {
        const { data } = await api.get<Application>(`/applications/${id}`)
        if (!active) return
        setItem(data)

        try {
          const hist = await api.get<ApplicationHistoryEntry[]>(
            `/applications/${id}/history`,
          )
          if (active) {
            setHistory(Array.isArray(hist.data) ? hist.data : [])
          }
        } catch {
          if (active) setHistory([])
        }
      } catch {
        if (active) setError('Не удалось загрузить заявку.')
      } finally {
        if (active) setLoading(false)
      }
    }

    void load()

    return () => {
      active = false
    }
  }, [id])

  async function submitApplication() {
    setSubmitting(true)
    setError('')

    try {
      await api.post(`/applications/${id}/submit`)
      await loadAll()
    } catch {
      setError(
        'Не удалось отправить заявку. Проверьте поддержку этого действия на сервере.',
      )
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

            <span className={`status-pill ${statusClass(item.status)}`}>
              {statusLabel(item.status)}
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

              <div>
                <span>Продукт</span>
                <strong>
                  {item.credit_product_id != null
                    ? `#${item.credit_product_id}`
                    : 'Не указан'}
                </strong>
              </div>
            </div>
          </section>

          <section className="content-card application-details-card">
            <h2>Финансовая информация</h2>
            <div className="details-list">
              <div>
                <span>Ежемесячная выручка бизнеса</span>
                <strong>{formatMoney(item.monthly_income)}</strong>
              </div>

              <div>
                <span>Предварительный платёж</span>
                <strong>{formatMoney(item.preliminary_result)}</strong>
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
            </div>
          </section>

          <section className="content-card application-details-card">
            <h2>Информация о бизнесе</h2>
            <div className="details-list">
              <div>
                <span>Организационно-правовая форма</span>
                <strong>{formatLegalForm(item.legal_form)}</strong>
              </div>

              <div>
                <span>Название организации</span>
                <strong>{item.business_name || 'Не указано'}</strong>
              </div>

              <div>
                <span>Отрасль</span>
                <strong>{item.industry || 'Не указана'}</strong>
              </div>

              <div>
                <span>Регион</span>
                <strong>{item.region || 'Не указан'}</strong>
              </div>

              <div>
                <span>Дата начала деятельности</span>
                <strong>{formatDateTime(item.business_start_date)}</strong>
              </div>
            </div>
          </section>

          <section className="content-card application-details-card">
            <h2>Решение по заявке</h2>
            <div className="details-list">
              <div>
                <span>Статус</span>
                <strong>
                  <span className={`status-pill ${statusClass(item.status)}`}>
                    {statusLabel(item.status)}
                  </span>
                </strong>
              </div>
            </div>

            <div className="application-note">
              <strong>Комментарий по решению</strong>
              <p>
                {item.decision_comment ||
                  'Комментарий по решению отсутствует.'}
              </p>
            </div>

            <div className="application-note">
              <strong>Комментарий пользователя</strong>
              <p>{item.comment || 'Комментарий не добавлен.'}</p>
            </div>
          </section>

          <section className="content-card application-details-card">
            <h2>История статусов</h2>
            {history.length === 0 ? (
              <p>История пуста.</p>
            ) : (
              <div className="history-list">
                {history.map((h) => (
                  <div className="history-row" key={h.id}>
                    <span>{formatDateTime(h.created_at)}</span>
                    <span className="transition">
                      {h.old_status
                        ? statusLabel(h.old_status)
                        : '—'}{' '}
                      → {statusLabel(h.new_status)}
                    </span>
                    <span className="comment">{h.comment || ''}</span>
                  </div>
                ))}
              </div>
            )}
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

          {item.status === 'draft' && (
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