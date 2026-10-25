import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import PageLayout from '../components/layout/PageLayout'
import Loader from '../components/ui/Loader'
import ProductCard from '../features/products/ProductCard'
import type { CreditProduct } from '../features/products/productsTypes'
import { api } from "../services/apiClients"

export default function ProductsPage() {
  const [products, setProducts] = useState<CreditProduct[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    api.get('/products')
      .then(({ data }) => {
        const items = Array.isArray(data) ? data : data.items ?? data.products ?? []
        if (active) setProducts(items)
      })
      .catch(() => {
        if (active) setError('Не удалось загрузить продукты. Проверьте API-сервер.')
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
        <span className="eyebrow">Каталог</span>
        <h1>Выберите кредитный продукт</h1>
        <p>Сравните условия и выберите подходящее предложение.</p>
      </div>

      {loading && <Loader text="Загружаем кредитные продукты..." />}

      {error && <div className="notice">{error}</div>}

      {!loading && !error && products.length === 0 && (
        <div className="content-card">
          <h2>Пока нет продуктов</h2>
          <p>Когда предложения появятся на сервере, они отобразятся здесь.</p>
        </div>
      )}

      {!loading && products.length > 0 && (
        <div className="product-grid">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}

      <p>
        <Link to="/applications/new">Перейти к созданию заявки</Link>
      </p>
    </PageLayout>
  )
}