export type UserRole = 'client' | 'staff' | 'admin'

export type User = {
  id: number
  email: string
  role: UserRole
  created_at: string
}

export type CreditProduct = {
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
  created_at: string
  updated_at: string
}

export type ApplicationStatus =
  | 'draft'
  | 'submitted'
  | 'checking'
  | 'approved'
  | 'rejected'
  | 'needs_info'
  | 'alternative_offer'

export type Application = {
  id: number
  user_id: number
  credit_product_id: number
  amount: number | string
  term_months: number
  purpose: string
  monthly_income: number | string
  employment: string
  status: ApplicationStatus
  comment: string | null
  decision_comment: string | null
  preliminary_result: number | string | null
  monthly_payment: number | string | null
  total_payment: number | string | null
  overpayment: number | string | null
  created_at: string
  updated_at: string
}

export type ApplicationCreate = {
  credit_product_id: number
  amount: number
  term_months: number
  purpose: string
  monthly_income: number
  employment: string
}

export type ApplicationUpdate = Partial<ApplicationCreate>

export type ApplicationHistoryEntry = {
  id: number
  application_id: number
  old_status: string | null
  new_status: string
  comment: string | null
  created_at: string
}

export type BusinessProfile = {
  id: number
  user_id: number
  business_name: string
  legal_form: string
  industry: string
  region: string
  business_start_date: string
  monthly_revenue: number | string
  created_at: string
  updated_at: string
}

export type BusinessProfileUpsert = {
  business_name: string
  legal_form: string
  industry: string
  region: string
  business_start_date: string
  monthly_revenue: number
}

export type RecommendationItem = {
  id: number
  product_id: number
  match_score: number | string
  estimated_monthly_payment: number | string
  reasons: string[]
}

export type Recommendation = {
  id: number
  user_id: number
  requested_amount: number | string
  term_months: number
  purpose: string
  monthly_revenue: number | string
  business_age_months: number
  created_at: string
  items: RecommendationItem[]
}

export type RecommendationRequest = {
  requested_amount: number
  term_months: number
  purpose: string
  monthly_revenue: number
  business_age_months: number
}

export type CreditCalculation = {
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
  disclaimer: string
}

export type CreditComparison = {
  amount: number | string
  term_months: number
  products: CreditCalculation[]
}

export type CreditCalculationRequest = {
  product_id: number
  amount: number
  term_months: number
}

export type CreditComparisonRequest = {
  amount: number
  term_months: number
}