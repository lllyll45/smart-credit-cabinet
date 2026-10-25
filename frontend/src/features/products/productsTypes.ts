import type { CreditProduct } from '../../types/comon'

export type { CreditProduct }

export interface CreditCalculation {
  monthlyPayment: number
  totalPayment: number
  overpayment: number
}