import { Link } from 'react-router-dom'
import type { CreditProduct } from './productsTypes'
import { formatCurrency } from '../../utils/formatCurrency'

type ProductCardProps = {
  product: CreditProduct
}

export default function ProductCard({ product }: ProductCardProps) {
  const id = String(product.id)

  return (
    <article className="content-card product-card">
      <div className="product-rate">
        {product.interest_rate != null
          ? `${product.interest_rate}%`
          : 'Ставка уточняется'}
      </div>

      <h3>{product.name}</h3>
      <p>{product.description || 'Подробности доступны на странице продукта.'}</p>

      <div className="details-list">
        {product.min_amount != null && (
          <div>
            <span>От</span>
            <strong>{formatCurrency(product.min_amount)}</strong>
          </div>
        )}
        {product.max_amount != null && (
          <div>
            <span>До</span>
            <strong>{formatCurrency(product.max_amount)}</strong>
          </div>
        )}
        {product.max_term_months != null && (
          <div>
            <span>Срок</span>
            <strong>{product.max_term_months} мес.</strong>
          </div>
        )}
      </div>

      <Link className="primary-button" to={`/products/${id}`}>
        Подробнее
      </Link>
    </article>
  )
}