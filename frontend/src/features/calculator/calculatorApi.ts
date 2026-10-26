import { api } from '../../services/apiClients'
import type {
  CreditCalculation,
  CreditCalculationRequest,
  CreditComparison,
  CreditComparisonRequest,
} from '../../types/comon'

export async function calculateProduct(
  payload: CreditCalculationRequest,
): Promise<CreditCalculation> {
  const { data } = await api.post<CreditCalculation>(
    '/calculator/calculate',
    payload,
  )
  return data
}

export async function compareProducts(
  payload: CreditComparisonRequest,
): Promise<CreditComparison> {
  const { data } = await api.post<CreditComparison>(
    '/calculator/compare',
    payload,
  )
  return data
}