
from decimal import Decimal, ROUND_HALF_UP


CENT = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    """Округление денежной суммы до копеек."""
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def calculate_credit(
    amount: Decimal,
    annual_rate: Decimal,
    term_months: int,
) -> dict[str, Decimal]:
    """
    Рассчитывает аннуитетный платёж, общую сумму выплат
    и переплату по процентам.

    Комиссии пока не учитываются.
    """
    if amount <= 0:
        raise ValueError("Сумма кредита должна быть положительной")

    if annual_rate < 0:
        raise ValueError("Процентная ставка не может быть отрицательной")

    if term_months <= 0:
        raise ValueError("Срок кредита должен быть положительным")

    monthly_rate = annual_rate / Decimal("1200")

    if monthly_rate == 0:
        monthly_payment = amount / Decimal(term_months)
    else:
        factor = (Decimal("1") + monthly_rate) ** term_months

        monthly_payment = (
            amount
            * monthly_rate
            * factor
            / (factor - Decimal("1"))
        )

    monthly_payment = money(monthly_payment)
    total_payment = money(monthly_payment * term_months)
    overpayment = money(total_payment - amount)

    return {
        "monthly_payment": monthly_payment,
        "total_payment": total_payment,
        "overpayment": overpayment,
    }
