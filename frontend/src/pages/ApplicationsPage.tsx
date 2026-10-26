import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import PageLayout from '../components/layout/PageLayout'
import Loader from '../components/ui/Loader'
import { formatCurrency } from '../utils/formatCurrency'
import { formatDate } from '../utils/formatDate'
import { api } from '../services/apiClients'
import { statusClass, statusLabel } from '../features/applications/statuses'
import type { Application, CreditProduct } from '../types/comon'

export default function ApplicationsPage() {
  const [items, setItems] = useState<Application[]>([])
  const [products, setProducts] = useState<Record<number, string>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    Promise.all([
      api.get<Application[]>('/applications'),
      api.get<CreditProduct[]>('/products'),
    ])
      .then(([appsRes, productsRes]) => {
        if (!active) return

        const apps = Array.isArray(appsRes.data) ? appsRes.data : []
        setItems(apps)

        const productMap: Record<number, string> = {}
        for (const p of productsRes.data) {
          productMap[p.id] = `${p.bank_name} — ${p.name}`
        }
        setProducts(productMap)
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
                <p>
                  {products[item.credit_product_id] ??
                    `Продукт #${item.credit_product_id}`}
                </p>
                {item.created_at && (
                  <small>{formatDate(item.created_at)}</small>
                )}
              </div>
              <div>
                {item.amount != null && (
                  <strong>{formatCurrency(item.amount)}</strong>
                )}
                <span className={`status-pill ${statusClass(item.status)}`}>
                  {statusLabel(item.status)}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </PageLayout>
  )
}