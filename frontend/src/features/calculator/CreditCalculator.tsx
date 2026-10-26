import { useEffect, useState, type FormEvent } from 'react'
import Input from '../../components/ui/Input'
import Button from '../../components/ui/Button'
import { api } from '../../services/apiClients'
import { calculateProduct } from './calculatorApi'
import { formatCurrency } from '../../utils/formatCurrency'
import { getErrorMessage } from '../../utils/getErrorMessage'
import type {
  CreditCalculation,
  CreditProduct,
} from '../../types/comon'

export default function CreditCalculator() {
  const [products, setProducts] = useState<CreditProduct[]>([])
  const [productId, setProductId] = useState('')
  const [amount, setAmount] = useState('500000')
  const [term, setTerm] = useState('36')
  const [result, setResult] = useState<CreditCalculation | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api
      .get<CreditProduct[]>('/products')
      .then(({ data }) => {
        const active = data.filter((p) => p.is_active !== false)
        setProducts(active)
        if (active.length > 0) setProductId(String(active[0].id))
      })
      .catch((err) => setError(getErrorMessage(err)))
  }, [])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setResult(null)
    setLoading(true)
    try {
      const calc = await calculateProduct({
        product_id: Number(productId),
        amount: Number(amount),
        term_months: Number(term),
      })
      setResult(calc)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="content-card">
      <div className="section-heading">
        <h2>Кредитный калькулятор</h2>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-field">
            <label htmlFor="calc-product">Кредитный продукт</label>
            <select
              id="calc-product"
              className="input"
              value={productId}
              onChange={(e) => setProductId(e.target.value)}
              required
            >
              {products.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.bank_name} — {p.name}
                </option>
              ))}
            </select>
          </div>

          <Input
            label="Сумма кредита, ₽"
            type="number"
            min="1"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />
          <Input
            label="Срок, месяцев"
            type="number"
            min="1"
            max="600"
            value={term}
            onChange={(e) => setTerm(e.target.value)}
          />
        </div>

        {error && <p className="form-error">{error}</p>}

        {result && (
          <div className="notice">
            <p>
              Ставка: <strong>{result.interest_rate}%</strong>
            </p>
            <p>
              Ежемесячный платёж:{' '}
              <strong>{formatCurrency(result.monthly_payment)}</strong>
            </p>
            <p>
              Общая сумма:{' '}
              <strong>{formatCurrency(result.total_payment)}</strong>
            </p>
            <p>
              Переплата:{' '}
              <strong>{formatCurrency(result.overpayment)}</strong>
            </p>
            <p>
              Комиссия:{' '}
              <strong>{formatCurrency(result.commission)}</strong>
            </p>
            <p>{result.disclaimer}</p>
          </div>
        )}

        <Button type="submit" loading={loading} className="button-spaced">
          Рассчитать
        </Button>
      </form>
    </section>
  )
}