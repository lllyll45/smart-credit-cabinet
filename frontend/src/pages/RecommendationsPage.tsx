import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import PageLayout from '../components/layout/PageLayout'
import Input from '../components/ui/Input'
import Select from '../components/ui/Select'
import Button from '../components/ui/Button'
import { createRecommendation } from '../features/recommendations/recommendationsApi'
import { formatCurrency } from '../utils/formatCurrency'
import { getErrorMessage } from '../utils/getErrorMessage'
import type { Recommendation } from '../types/comon'

const PURPOSE_OPTIONS = [
  { value: 'working_capital', label: 'Пополнение оборотных средств' },
  { value: 'business_expansion', label: 'Развитие бизнеса' },
  { value: 'equipment', label: 'Покупка оборудования' },
]

export default function RecommendationsPage() {
  const [requestedAmount, setRequestedAmount] = useState('1000000')
  const [termMonths, setTermMonths] = useState('36')
  const [purpose, setPurpose] = useState('')
  const [monthlyRevenue, setMonthlyRevenue] = useState('300000')
  const [businessAge, setBusinessAge] = useState('24')

  const [result, setResult] = useState<Recommendation | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setResult(null)

    const amount = Number(requestedAmount)
    const term = Number(termMonths)
    const revenue = Number(monthlyRevenue)
    const age = Number(businessAge)

    if (!Number.isFinite(amount) || amount <= 0) {
      setError('Укажите корректную сумму.')
      return
    }
    if (!Number.isInteger(term) || term <= 0) {
      setError('Укажите корректный срок в месяцах.')
      return
    }
    if (!Number.isFinite(revenue) || revenue <= 0) {
      setError('Укажите корректную выручку.')
      return
    }
    if (!Number.isInteger(age) || age < 0) {
      setError('Укажите корректный возраст бизнеса.')
      return
    }
    if (!purpose.trim()) {
      setError('Выберите цель кредита.')
      return
    }

    setLoading(true)
    try {
      const data = await createRecommendation({
        requested_amount: amount,
        term_months: term,
        purpose: purpose.trim(),
        monthly_revenue: revenue,
        business_age_months: age,
      })
      setResult(data)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  const sortedItems = result
    ? [...result.items].sort(
        (a, b) => Number(b.match_score) - Number(a.match_score),
      )
    : []

  return (
    <PageLayout>
      <div className="page-heading">
        <span className="eyebrow">Подбор</span>
        <h1>Подбор кредитных предложений</h1>
        <p>
          Заполните параметры — подберём продукты по взвешенному
          match_score.
        </p>
      </div>

      <section className="content-card">
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <Input
              label="Сумма кредита, ₽"
              type="number"
              min="1"
              value={requestedAmount}
              onChange={(e) => setRequestedAmount(e.target.value)}
            />
            <Input
              label="Срок, месяцев"
              type="number"
              min="1"
              max="600"
              value={termMonths}
              onChange={(e) => setTermMonths(e.target.value)}
            />
            <Input
              label="Ежемесячная выручка, ₽"
              type="number"
              min="1"
              value={monthlyRevenue}
              onChange={(e) => setMonthlyRevenue(e.target.value)}
            />
            <Input
              label="Возраст бизнеса, месяцев"
              type="number"
              min="0"
              value={businessAge}
              onChange={(e) => setBusinessAge(e.target.value)}
            />
            <Select
              id="reco-purpose"
              label="Цель кредита"
              name="purpose"
              options={PURPOSE_OPTIONS}
              value={purpose}
              onChange={(e) => setPurpose(e.target.value)}
              required
            />
          </div>

          {error && <p className="form-error">{error}</p>}

          <Button
            type="submit"
            loading={loading}
            className="button-spaced"
          >
            Подобрать предложения
          </Button>
        </form>
      </section>

      {result && (
        <section className="section-block">
          <div className="section-heading">
            <h2>Результаты подбора</h2>
            <span>{sortedItems.length} предложений</span>
          </div>

          {sortedItems.length === 0 && (
            <div className="content-card">
              <p>Для ваших параметров подходящих продуктов не найдено.</p>
            </div>
          )}

          <div className="comparison-list">
            {sortedItems.map((item) => {
              const score = Number(item.match_score)
              const percent = Math.max(0, Math.min(100, score))
              return (
                <article
                  className="content-card comparison-card"
                  key={item.id}
                >
                  <div className="comparison-title">
                    <div className="rank-badge">
                      {Math.round(score)}
                    </div>
                    <div style={{ flex: 1 }}>
                      <h3>Продукт #{item.product_id}</h3>
                      <p>
                        Оценочный платёж:{' '}
                        <strong>
                          {formatCurrency(
                            item.estimated_monthly_payment,
                          )}
                        </strong>
                      </p>
                    </div>
                    <span className="score-badge">
                      {Math.round(score)} / 100
                    </span>
                  </div>

                  <div className="score-meter" aria-hidden="true">
                    <span style={{ width: `${percent}%` }} />
                  </div>

                  {item.reasons.length > 0 && (
                    <div className="reasons-chips">
                      {item.reasons.map((reason, i) => (
                        <span key={i} className="reason-chip">
                          {reason}
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="button-spaced">
                    <Link
                      className="primary-button"
                      to={`/applications/new?productId=${item.product_id}`}
                    >
                      Подать заявку
                    </Link>
                  </div>
                </article>
              )
            })}
          </div>
        </section>
      )}
    </PageLayout>
  )
}