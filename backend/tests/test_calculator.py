
from decimal import Decimal

import pytest

from app.services.calculator import calculate_credit


def test_calculate_credit_without_interest():
    result = calculate_credit(
        amount=Decimal("120000"),
        annual_rate=Decimal("0"),
        term_months=12,
    )

    assert result["monthly_payment"] == Decimal("10000.00")
    assert result["total_payment"] == Decimal("120000.00")
    assert result["overpayment"] == Decimal("0.00")


def test_calculate_credit_with_interest():
    result = calculate_credit(
        amount=Decimal("120000"),
        annual_rate=Decimal("12"),
        term_months=12,
    )

    assert result["monthly_payment"] == Decimal("10661.85")
    assert result["total_payment"] == Decimal("127942.20")
    assert result["overpayment"] == Decimal("7942.20")


@pytest.mark.parametrize(
    ("amount", "annual_rate", "term_months"),
    [
        (Decimal("0"), Decimal("12"), 12),
        (Decimal("-1000"), Decimal("12"), 12),
        (Decimal("1000"), Decimal("-1"), 12),
        (Decimal("1000"), Decimal("12"), 0),
        (Decimal("1000"), Decimal("12"), -1),
    ],
)
def test_calculate_credit_rejects_invalid_input(
    amount,
    annual_rate,
    term_months,
):
    with pytest.raises(ValueError):
        calculate_credit(amount, annual_rate, term_months)
