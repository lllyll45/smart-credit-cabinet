import { Link } from 'react-router-dom'
import type { CreditProduct } from '../../types/comon'
import { formatCurrency } from '../../utils/formatCurrency'

type ProductCardProps = {
  product: CreditProduct
}

export default function ProductCard({ product }: ProductCardProps) {
  return (
    <article className="content-card product-card">
      <div className="product-rate">
        {product.interest_rate != null
          ? `${product.interest_rate}%`
          : 'Ставка уточняется'}
      </div>

      <h3>{product.name}</h3>
      <p className="product-conditions">
        {product.bank_name}
        {product.additional_conditions
          ? ` · ${product.additional_conditions}`
          : ''}
      </p>

      <div className="details-list">
        <div>
          <span>От</span>
          <strong>{formatCurrency(product.min_amount)}</strong>
        </div>
        <div>
          <span>До</span>
          <strong>{formatCurrency(product.max_amount)}</strong>
        </div>
        <div>
          <span>Срок</span>
          <strong>до {product.max_term_months} мес.</strong>
        </div>
      </div>

      <Link className="primary-button" to={`/products/${product.id}`}>
        Подробнее
      </Link>
    </article>
  )
}