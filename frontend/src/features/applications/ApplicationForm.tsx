import { useEffect, useState, type FormEvent } from 'react'
import { useSearchParams } from 'react-router-dom'
import Input from '../../components/ui/Input'
import Button from '../../components/ui/Button'
import { api } from '../../services/apiClients'
import type { ApplicationCreate, CreditProduct } from '../../types/comon'

export type ApplicationFormValues = ApplicationCreate

type ApplicationFormProps = {
  productId?: number
  onSubmit: (values: ApplicationFormValues) => Promise<void>
}

export default function ApplicationForm({
  productId,
  onSubmit,
}: ApplicationFormProps) {
  const [searchParams] = useSearchParams()

  const queryProductId = Number(searchParams.get('productId'))
  const initialProductId =
    productId ?? (queryProductId > 0 ? queryProductId : undefined)

  const [products, setProducts] = useState<CreditProduct[]>([])
  const [selectedProductId, setSelectedProductId] = useState(
    initialProductId ? String(initialProductId) : '',
  )
  const [amount, setAmount] = useState('500000')
  const [term, setTerm] = useState('36')
  const [purpose, setPurpose] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [loadingProducts, setLoadingProducts] = useState(true)

  useEffect(() => {
    let cancelled = false

    async function loadProducts() {
      try {
        const { data } = await api.get<CreditProduct[]>('/products')
        if (cancelled) return

        const activeProducts = data.filter((p) => p.is_active !== false)
        setProducts(activeProducts)

        setSelectedProductId((prev) => {
          if (
            initialProductId &&
            activeProducts.some((p) => p.id === initialProductId)
          ) {
            return String(initialProductId)
          }

          if (prev && activeProducts.some((p) => String(p.id) === prev)) {
            return prev
          }

          return activeProducts[0] ? String(activeProducts[0].id) : ''
        })
      } catch {
        if (!cancelled) {
          setError(
            'Не удалось загрузить кредитные продукты. Обновите страницу.',
          )
        }
      } finally {
        if (!cancelled) setLoadingProducts(false)
      }
    }

    void loadProducts()

    return () => {
      cancelled = true
    }
  }, [initialProductId])

  const selectedProduct = products.find(
    (p) => p.id === Number(selectedProductId),
  )

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')

    const parsedProductId = Number(selectedProductId)
    const parsedAmount = Number(amount)
    const parsedTerm = Number(term)

    if (!selectedProduct) {
      setError('Выберите кредитный продукт.')
      return
    }

    if (!Number.isFinite(parsedAmount) || parsedAmount <= 0) {
      setError('Введите корректную сумму кредита.')
      return
    }

    if (
      parsedAmount < Number(selectedProduct.min_amount) ||
      parsedAmount > Number(selectedProduct.max_amount)
    ) {
      setError(
        `Сумма должна быть от ${selectedProduct.min_amount} до ${selectedProduct.max_amount} ₽.`,
      )
      return
    }

    if (
      !Number.isInteger(parsedTerm) ||
      parsedTerm < selectedProduct.min_term_months ||
      parsedTerm > selectedProduct.max_term_months
    ) {
      setError(
        `Срок должен быть от ${selectedProduct.min_term_months} до ${selectedProduct.max_term_months} месяцев.`,
      )
      return
    }

    if (purpose.trim().length < 3) {
      setError('Укажите цель кредита (не менее 3 символов).')
      return
    }

    setSubmitting(true)

    try {
      await onSubmit({
        credit_product_id: parsedProductId,
        amount: parsedAmount,
        term_months: parsedTerm,
        purpose: purpose.trim(),
      })
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Не удалось создать заявку.',
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form className="content-card" onSubmit={handleSubmit}>
      <div className="section-heading">
        <div>
          <p className="eyebrow">Кредитование бизнеса</p>
          <h2>Параметры кредитной заявки</h2>
        </div>
      </div>

      {loadingProducts ? (
        <p>Загружаем кредитные продукты...</p>
      ) : products.length === 0 ? (
        <p className="form-error">
          Нет доступных кредитных продуктов. Проверьте подключение к API.
        </p>
      ) : (
        <>
          <div className="form-grid">
            <div className="form-field">
              <label htmlFor="credit-product">Кредитный продукт</label>
              <select
                id="credit-product"
                className="input"
                value={selectedProductId}
                onChange={(event) => setSelectedProductId(event.target.value)}
                required
              >
                <option value="">Выберите продукт</option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.bank_name} — {product.name}
                  </option>
                ))}
              </select>
            </div>

            <Input
              label="Сумма кредита, ₽"
              type="number"
              min={selectedProduct?.min_amount ?? 1}
              max={selectedProduct?.max_amount}
              value={amount}
              onChange={(event) => setAmount(event.target.value)}
              required
            />

            <Input
              label="Срок кредита, месяцев"
              type="number"
              min={selectedProduct?.min_term_months ?? 1}
              max={selectedProduct?.max_term_months ?? 360}
              value={term}
              onChange={(event) => setTerm(event.target.value)}
              required
            />

            <div className="form-field">
              <label htmlFor="purpose">Цель кредитования бизнеса</label>
              <textarea
                id="purpose"
                className="input"
                rows={3}
                value={purpose}
                onChange={(event) => setPurpose(event.target.value)}
                placeholder="Например, закупка оборудования или пополнение оборотных средств"
                required
              />
            </div>
          </div>

          <p className="notice">
            Данные организации и среднемесячная выручка берутся из профиля
            бизнеса.
          </p>

          {selectedProduct && (
            <p className="notice">
              Доступная сумма: {selectedProduct.min_amount}–
              {selectedProduct.max_amount} ₽. Срок:{' '}
              {selectedProduct.min_term_months}–
              {selectedProduct.max_term_months} месяцев.
            </p>
          )}

          {error && (
            <p className="form-error" role="alert">
              {error}
            </p>
          )}

          <Button type="submit" disabled={submitting}>
            {submitting ? 'Создание заявки...' : 'Создать заявку'}
          </Button>
        </>
      )}
    </form>
  )
}

