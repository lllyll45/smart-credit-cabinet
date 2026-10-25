import type { CreditCalculation } from '../products/productsTypes'

export function calculateCredit(
  amount: number,
  annualRate: number,
  months: number,
): CreditCalculation {
  if (
    !Number.isFinite(amount) ||
    !Number.isFinite(annualRate) ||
    !Number.isFinite(months) ||
    amount <= 0 ||
    annualRate < 0 ||
    months <= 0
  ) {
    throw new Error('Проверьте сумму, процентную ставку и срок.')
  }

  const monthlyRate = annualRate / 100 / 12

  const monthlyPayment =
    monthlyRate === 0
      ? amount / months
      : (amount * monthlyRate) /
        (1 - Math.pow(1 + monthlyRate, -months))

  const totalPayment = monthlyPayment * months

  return {
    monthlyPayment,
    totalPayment,
    overpayment: totalPayment - amount,
  }
}