import { useState } from 'react'
import { calculateCredit } from './calculator'
import { formatCurrency } from '../../utils/formatCurrency'
import Input from '../../components/ui/Input'

export default function CreditCalculator() {
  const [amount, setAmount] = useState('500000')
  const [rate, setRate] = useState('15')
  const [months, setMonths] = useState('36')

  const principal = Number(amount)
  const annualRate = Number(rate)
  const term = Number(months)

  const valid =
    principal > 0 &&
    annualRate >= 0 &&
    term > 0 &&
    Number.isFinite(principal) &&
    Number.isFinite(annualRate) &&
    Number.isFinite(term)

  const result = valid
    ? calculateCredit(principal, annualRate, term)
    : null

  return (
    <section className="content-card">
      <div className="section-heading">
        <h2>Кредитный калькулятор</h2>
      </div>

      <div className="form-grid">
        <Input
          label="Сумма кредита, ₽"
          type="number"
          min="1"
          value={amount}
          onChange={(event) => setAmount(event.target.value)}
        />
        <Input
          label="Годовая ставка, %"
          type="number"
          min="0"
          step="0.1"
          value={rate}
          onChange={(event) => setRate(event.target.value)}
        />
        <Input
          label="Срок, месяцев"
          type="number"
          min="1"
          max="600"
          value={months}
          onChange={(event) => setMonths(event.target.value)}
        />
      </div>

      {result ? (
        <div className="notice">
          <p>
            Ежемесячный платёж:{' '}
            <strong>{formatCurrency(result.monthlyPayment)}</strong>
          </p>
          <p>
            Общая сумма выплат:{' '}
            <strong>{formatCurrency(result.totalPayment)}</strong>
          </p>
          <p>
            Переплата: <strong>{formatCurrency(result.overpayment)}</strong>
          </p>
        </div>
      ) : (
        <p className="form-error">Введите корректные сумму, ставку и срок.</p>
      )}

      <p>
        Расчёт предварительный. Фактические условия определяются кредитором.
      </p>
    </section>
  )
}