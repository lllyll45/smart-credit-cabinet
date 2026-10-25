"""Граничные случаи денежных расчётов."""

from decimal import Decimal

import pytest

from app.services.calculator import calculate_credit, money


def test_money_rounding_half_up():
    assert money(Decimal("0.005")) == Decimal("0.01")
    assert money(Decimal("0.004")) == Decimal("0.00")


def test_zero_rate_returns_exact_division():
    result = calculate_credit(
        amount=Decimal("120000"), annual_rate=Decimal("0"), term_months=12
    )
    assert result["monthly_payment"] == Decimal("10000.00")
    assert result["total_payment"] == Decimal("120000.00")
    assert result["overpayment"] == Decimal("0.00")


def test_large_amount_rounds_correctly():
    result = calculate_credit(
        amount=Decimal("10000000"),
        annual_rate=Decimal("19.90"),
        term_months=60,
    )
    assert result["monthly_payment"] > Decimal("0")
    assert result["total_payment"] >= result["monthly_payment"] * 60 - Decimal("1")
    assert result["total_payment"] <= result["monthly_payment"] * 60 + Decimal("1")


def test_last_payment_does_not_exceed_total():
    result = calculate_credit(
        amount=Decimal("100000"),
        annual_rate=Decimal("15"),
        term_months=12,
    )
    total = result["total_payment"]
    monthly = result["monthly_payment"]
    assert total <= monthly * 12
    assert total > monthly * 11


def test_overpayment_matches_total_minus_amount():
    result = calculate_credit(
        amount=Decimal("100000"),
        annual_rate=Decimal("15"),
        term_months=12,
    )
    assert result["overpayment"] == result["total_payment"] - Decimal("100000")


@pytest.mark.parametrize(
    ("amount", "rate", "term"),
    [
        (Decimal("0"), Decimal("10"), 12),
        (Decimal("-1"), Decimal("10"), 12),
        (Decimal("1000"), Decimal("-1"), 12),
        (Decimal("1000"), Decimal("10"), 0),
    ],
)
def test_invalid_inputs_raise(amount, rate, term):
    with pytest.raises(ValueError):
        calculate_credit(amount, rate, term)