import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import PageLayout from '../components/layout/PageLayout'
import Loader from '../components/ui/Loader'
import Button from '../components/ui/Button'
import Modal from '../components/ui/Modal'
import Input from '../components/ui/Input'
import { formatCurrency } from '../utils/formatCurrency'
import { formatDate } from '../utils/formatDate'
import { getErrorMessage } from '../utils/getErrorMessage'
import {
  approveApplication,
  fetchStaffApplications,
  offerAlternative,
  rejectApplication,
  requestMoreInfo,
  startChecking,
} from '../features/staff/staffApi'
import {
  STATUS_LABELS,
  STATUS_ORDER,
  statusClass,
  statusLabel,
} from '../features/applications/statuses'
import type {
  Application,
  ApplicationStatus,
} from '../types/comon'

export default function StaffApplicationsPage() {
  const [items, setItems] = useState<Application[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionBusy, setActionBusy] = useState<number | null>(null)
  const [activeTab, setActiveTab] = useState<ApplicationStatus | 'all'>(
    'all',
  )

  const [rejectId, setRejectId] = useState<number | null>(null)
  const [rejectReason, setRejectReason] = useState('')

  async function reload() {
    const data = await fetchStaffApplications()
    setItems(data)
  }

  useEffect(() => {
    let active = true
    fetchStaffApplications()
      .then((data) => {
        if (active) setItems(data)
      })
      .catch((err) => {
        if (active) setError(getErrorMessage(err))
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [])

  async function runAction(id: number, fn: () => Promise<Application>) {
    setError('')
    setActionBusy(id)
    try {
      await fn()
      await reload()
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setActionBusy(null)
    }
  }

  async function submitReject() {
    if (rejectId == null) return
    if (!rejectReason.trim()) {
      setError('Укажите причину отказа.')
      return
    }
    setError('')
    setActionBusy(rejectId)
    try {
      await rejectApplication(rejectId, rejectReason.trim())
      setRejectId(null)
      setRejectReason('')
      await reload()
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setActionBusy(null)
    }
  }

  const filtered =
    activeTab === 'all'
      ? items
      : items.filter((i) => i.status === activeTab)

  return (
    <PageLayout>
      <div className="page-heading">
        <span className="eyebrow">Staff</span>
        <h1>Заявки клиентов</h1>
        <p>Проверка и решения по кредитным заявкам.</p>
      </div>

      <div className="tabs">
        <button
          type="button"
          className={activeTab === 'all' ? 'active' : ''}
          onClick={() => setActiveTab('all')}
        >
          Все ({items.length})
        </button>
        {STATUS_ORDER.filter(
          (s) => s !== 'draft' && s !== 'submitted',
        ).map((s) => {
          const count = items.filter((i) => i.status === s).length
          return (
            <button
              key={s}
              type="button"
              className={activeTab === s ? 'active' : ''}
              onClick={() => setActiveTab(s)}
            >
              {STATUS_LABELS[s]} ({count})
            </button>
          )
        })}
        {items.some((i) => i.status === 'submitted') && (
          <button
            type="button"
            className={activeTab === 'submitted' ? 'active' : ''}
            onClick={() => setActiveTab('submitted')}
          >
            Отправлены (
            {items.filter((i) => i.status === 'submitted').length})
          </button>
        )}
      </div>

      {loading && <Loader text="Загружаем заявки..." />}
      {error && <p className="form-error">{error}</p>}

      {!loading && filtered.length === 0 && (
        <div className="content-card">
          <p>Заявок в этой категории нет.</p>
        </div>
      )}

      <div className="application-list">
        {filtered.map((app) => (
          <article
            key={app.id}
            className="content-card application-details-card"
          >
            <div className="application-detail-heading">
              <div>
                <span className="eyebrow">
                  Заявка №{app.id} · пользователь #{app.user_id}
                </span>
                <h3 style={{ margin: '6px 0 4px' }}>
                  {formatCurrency(app.amount)}
                </h3>
                <p>
                  Срок: {app.term_months} мес. · Продукт #
                  {app.credit_product_id}
                </p>
                <p>{formatDate(app.created_at)}</p>
              </div>
              <span
                className={`status-pill ${statusClass(app.status)}`}
              >
                {statusLabel(app.status)}
              </span>
            </div>

            <div className="details-list">
              <div>
                <span>Доход</span>
                <strong>{formatCurrency(app.monthly_income)}</strong>
              </div>
              <div>
                <span>Цель</span>
                <strong>{app.purpose || '—'}</strong>
              </div>
              <div>
                <span>Предв. платёж</span>
                <strong>
                  {app.preliminary_result != null
                    ? formatCurrency(app.preliminary_result)
                    : '—'}
                </strong>
              </div>
            </div>

            <div
              className="button-spaced"
              style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}
            >
              <Link
                className="secondary-button"
                to={`/applications/${app.id}`}
              >
                Открыть
              </Link>

              {(app.status === 'submitted' ||
                app.status === 'needs_info') && (
                <Button
                  loading={actionBusy === app.id}
                  onClick={() =>
                    runAction(app.id, () => startChecking(app.id))
                  }
                >
                  Начать проверку
                </Button>
              )}

              {app.status === 'checking' && (
                <>
                  <Button
                    variant="secondary"
                    loading={actionBusy === app.id}
                    onClick={() =>
                      runAction(app.id, () =>
                        requestMoreInfo(app.id),
                      )
                    }
                  >
                    Запросить уточнения
                  </Button>
                  <Button
                    variant="secondary"
                    loading={actionBusy === app.id}
                    onClick={() =>
                      runAction(app.id, () =>
                        offerAlternative(app.id),
                      )
                    }
                  >
                    Альтернатива
                  </Button>
                  <Button
                    loading={actionBusy === app.id}
                    onClick={() =>
                      runAction(app.id, () =>
                        approveApplication(app.id),
                      )
                    }
                  >
                    Одобрить
                  </Button>
                  <Button
                    variant="danger"
                    loading={actionBusy === app.id}
                    onClick={() => {
                      setRejectId(app.id)
                      setRejectReason('')
                    }}
                  >
                    Отклонить
                  </Button>
                </>
              )}
            </div>
          </article>
        ))}
      </div>

      <Modal
        open={rejectId !== null}
        title="Причина отказа"
        onClose={() => {
          setRejectId(null)
          setRejectReason('')
        }}
      >
        <Input
          label="Причина отказа"
          value={rejectReason}
          onChange={(e) => setRejectReason(e.target.value)}
          placeholder="Например, недостаточный доход"
        />
        <div
          className="button-spaced"
          style={{ display: 'flex', gap: 10, marginTop: 16 }}
        >
          <Button
            variant="danger"
            onClick={submitReject}
            loading={actionBusy === rejectId}
          >
            Отклонить заявку
          </Button>
          <Button
            variant="secondary"
            onClick={() => {
              setRejectId(null)
              setRejectReason('')
            }}
          >
            Отмена
          </Button>
        </div>
      </Modal>
    </PageLayout>
  )
}