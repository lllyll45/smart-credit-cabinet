import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import PageLayout from '../components/layout/PageLayout'
import Loader from '../components/ui/Loader'
import { formatCurrency } from '../utils/formatCurrency'
import { api } from '../services/apiClients'
import type { CreditProduct } from '../types/comon'

export default function ProductDetailsPage() {
  const { id } = useParams()
  const [product, setProduct] = useState<CreditProduct | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    api
      .get<CreditProduct>(`/products/${id}`)
      .then(({ data }) => {
        if (active) setProduct(data)
      })
      .catch(() => {
        if (active)
          setError(
            'Не удалось загрузить продукт. Возможно, его не существует.',
          )
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [id])

  return (
    <PageLayout title="Информация о продукте">
      <p>
        <Link to="/products">← Все продукты</Link>
      </p>

      {loading && <Loader />}
      {error && <div className="notice">{error}</div>}

      {product && (
        <>
          <div className="page-heading">
            <span className="eyebrow">Кредитный продукт</span>
            <h1>{product.name}</h1>
            <p>
              {product.bank_name}
              {product.additional_conditions
                ? ` — ${product.additional_conditions}`
                : ''}
            </p>
          </div>

          <section className="content-card">
            <div className="details-list">
              <div>
                <span>Процентная ставка</span>
                <strong>
                  {product.interest_rate != null
                    ? `${product.interest_rate}% годовых`
                    : 'Не указана'}
                </strong>
              </div>
              <div>
                <span>Минимальная сумма</span>
                <strong>{formatCurrency(product.min_amount)}</strong>
              </div>
              <div>
                <span>Максимальная сумма</span>
                <strong>{formatCurrency(product.max_amount)}</strong>
              </div>
              <div>
                <span>Минимальный срок</span>
                <strong>{product.min_term_months} мес.</strong>
              </div>
              <div>
                <span>Максимальный срок</span>
                <strong>{product.max_term_months} мес.</strong>
              </div>
              {product.commission_rate != null && (
                <div>
                  <span>Комиссия</span>
                  <strong>{product.commission_rate}%</strong>
                </div>
              )}
              {product.commission_amount != null && (
                <div>
                  <span>Комиссия (фикс.)</span>
                  <strong>
                    {formatCurrency(product.commission_amount)}
                  </strong>
                </div>
              )}
              {product.additional_conditions && (
                <div>
                  <span>Доп. условия</span>
                  <strong>{product.additional_conditions}</strong>
                </div>
              )}
            </div>

            <Link
              className="primary-button full-button"
              to={`/applications/new?productId=${product.id}`}
            >
              Подать заявку
            </Link>
          </section>
        </>
      )}
    </PageLayout>
  )
}