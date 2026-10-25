import { api } from '../../services/apiClients'
import type { CreditProduct } from './productsTypes'

export async function fetchProducts(): Promise<CreditProduct[]> {
  const response = await api.get<CreditProduct[]>('/products')

  return Array.isArray(response.data) ? response.data : []
}

export async function fetchProduct(
  id: number,
): Promise<CreditProduct> {
  const response = await api.get<CreditProduct>(`/products/${id}`)
  return response.data
}