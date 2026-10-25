export type User = {
  id: number
  email: string
  created_at: string
}

export type CreditProduct = {
  description: string
  id: number
  name: string
  bank_name: string
  interest_rate: number | string
  min_amount: number | string
  max_amount: number | string
  min_term_months: number
  max_term_months: number
  commission_rate: number | string | null
  commission_amount: number | string | null
  additional_conditions: string | null
  is_active: boolean
}

export type Calculation = {
  product_id: number
  product_name: string
  bank_name: string
  interest_rate: number | string
  amount: number | string
  term_months: number
  monthly_payment: number | string
  total_payment: number | string
  overpayment: number | string
  commission: number | string
}

export type Application = {
  id: number
  user_id: number
  credit_product_id: number | null
  amount: number | string
  term_months: number
  purpose: string
  monthly_income: number | string
  employment: string
  status: string
  comment: string | null
  decision_comment: string | null
  monthly_payment: number | string | null
  total_payment: number | string | null
  overpayment: number | string | null
  created_at: string
  updated_at: string
}

export interface ApplicationCreate {
  product_id: number
  amount: number
  term_months: number
}