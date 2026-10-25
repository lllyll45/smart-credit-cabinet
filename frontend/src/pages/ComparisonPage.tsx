import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import PageLayout from '../components/layout/PageLayout'
import { compareProducts } from '../features/calculator/calculatorApi'
import { getErrorMessage } from '../utils/getErrorMessage'
import type {
  CreditCalculation,
  CreditComparison,
} from '../types/comon'

function money(value: string | number | undefined | null) {
  const number = Number(value)
  if (!Number.isFinite(number)) return '—'
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    maximumFractionDigits: 2,
  }).format(number)
}

export default function ComparisonPage() {
  const [amount, setAmount] = useState('1000000')
  const [term, setTerm] = useState('36')
  const [result, setResult] = useState<CreditComparison | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setResult(null)

    const amountValue = Number(amount)
    const termValue = Number(term)

    if (!Number.isFinite(amountValue) || amountValue <= 0) {
      setError('Укажите сумму кредита больше нуля.')
      return
    }

    if (!Number.isInteger(termValue) || termValue <= 0) {
      setError('Срок должен быть положительным числом месяцев.')
      return
    }

    setLoading(true)
    try {
      const data = await compareProducts({
        amount: amountValue,
        term_months: termValue,
      })
      setResult(data)

      if (!data.products || data.products.length === 0) {
        setError(
          'Для указанных параметров подходящие продукты не найдены.',
        )
      }
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  const sorted: CreditCalculation[] = result
    ? [...result.products].sort(
        (a, b) => Number(a.total_payment) - Number(b.total_payment),
      )
    : []

  return (
    <PageLayout>
      <section className="page-heading">
        <p className="eyebrow">Подбор финансирования</p>
        <h1>Сравнение кредитов</h1>
        <p>
          Сравните ежемесячный платёж, переплату и комиссию по
          предложениям банков.
        </p>
      </section>

      <section className="content-card">
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-field">
              <label htmlFor="compare-amount">Сумма кредита, ₽</label>
              <input
                id="compare-amount"
                name="amount"
                type="number"
                min="1"
                step="1"
                required
                value={amount}
                onChange={(event) => setAmount(event.target.value)}
              />
            </div>

            <div className="form-field">
              <label htmlFor="compare-term">Срок, месяцев</label>
              <input
                id="compare-term"
                name="term_months"
                type="number"
                min="1"
                step="1"
                required
                value={term}
                onChange={(event) => setTerm(event.target.value)}
              />
            </div>
          </div>

          <button
            className="primary-button"
            type="submit"
            disabled={loading}
          >
            {loading ? 'Сравниваем…' : 'Сравнить предложения'}
          </button>
        </form>

        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}
      </section>

      {result && sorted.length > 0 && (
        <section className="section-block">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Результаты расчёта</p>
              <h2>Доступные предложения</h2>
            </div>
            <span>{sorted.length} предложений</span>
          </div>

          <div className="product-grid">
            {sorted.map((product, index) => (
              <article
                className="content-card product-card"
                key={product.product_id}
              >
                <p className="eyebrow">
                  {index === 0
                    ? 'Наименьшая общая выплата'
                    : product.bank_name}
                </p>
                <h3>{product.product_name}</h3>
                <p>{product.bank_name}</p>

                <div className="product-rate">
                  {product.interest_rate}% годовых
                </div>

                <div className="details-list">
                  <div>
                    <span>Ежемесячный платёж</span>
                    <strong>{money(product.monthly_payment)}</strong>
                  </div>
                  <div>
                    <span>Общая выплата</span>
                    <strong>{money(product.total_payment)}</strong>
                  </div>
                  <div>
                    <span>Переплата</span>
                    <strong>{money(product.overpayment)}</strong>
                  </div>
                  <div>
                    <span>Комиссия</span>
                    <strong>{money(product.commission)}</strong>
                  </div>
                  <div>
                    <span>Срок</span>
                    <strong>{product.term_months} мес.</strong>
                  </div>
                </div>

                {product.disclaimer && (
                  <p className="product-conditions">
                    {product.disclaimer}
                  </p>
                )}

                <Link
                  className="primary-button full-button"
                  to={`/applications/new?productId=${product.product_id}`}
                >
                  Подать заявку
                </Link>
              </article>
            ))}
          </div>
        </section>
      )}
    </PageLayout>
  )
}