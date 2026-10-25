"""Recommendation scoring service."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.credit_product import CreditProduct
from app.services.calculator import calculate_credit


def _score_amount(
    amount: Decimal, min_amount: Decimal, max_amount: Decimal
) -> tuple[Decimal, str | None]:
    """Возвращает вес (0..1) и причину (или None, если не подходит)."""
    if amount < min_amount or amount > max_amount:
        return Decimal("0"), None
    return Decimal("1"), "Сумма входит в диапазон продукта"


def _score_term(
    term: int, min_term: int, max_term: int
) -> tuple[Decimal, str | None]:
    if term < min_term or term > max_term:
        return Decimal("0"), None
    return Decimal("1"), "Срок соответствует условиям продукта"


def _score_income(
    monthly_payment: Decimal | None, monthly_income: Decimal | None
) -> tuple[Decimal, str | None]:
    if monthly_payment is None or monthly_income is None or monthly_income <= 0:
        return Decimal("0.5"), "Доход не указан, оценка частичная"
    ratio = monthly_payment / monthly_income
    if ratio <= Decimal("0.40"):
        return Decimal("1"), "Платёж не превышает 40% дохода"
    if ratio <= Decimal("0.60"):
        return Decimal("0.5"), "Платёж составляет 40–60% дохода"
    return Decimal("0"), "Платёж превышает 60% дохода"


def _score_business_age(
    business_age_months: int | None, min_age_months: int | None
) -> tuple[Decimal, str | None]:
    if min_age_months is None:
        return Decimal("1"), None
    if business_age_months is None:
        return Decimal("0.5"), "Возраст бизнеса не указан"
    if business_age_months >= min_age_months:
        return Decimal("1"), "Возраст бизнеса соответствует требованиям"
    return Decimal("0"), None


def _score_purpose(
    purpose: str, supported: list[str]
) -> tuple[Decimal, str | None]:
    if not supported:
        return Decimal("1"), None
    if purpose in supported:
        return Decimal("1"), "Цель кредита поддерживается продуктом"
    return Decimal("0"), None


def build_recommendations(
    db: Session,
    requested_amount: Decimal,
    term_months: int,
    purpose: str,
    monthly_revenue: Decimal | None,
    business_age_months: int | None,
) -> list[dict]:
    """Возвращает список подходящих продуктов с оценкой."""

    products = db.scalars(
        select(CreditProduct).where(CreditProduct.is_active.is_(True))
    ).all()

    results: list[dict] = []

    for product in products:
        amount_score, amount_reason = _score_amount(
            requested_amount, product.min_amount, product.max_amount
        )
        if amount_score == 0:
            continue

        term_score, term_reason = _score_term(
            term_months, product.min_term_months, product.max_term_months
        )
        if term_score == 0:
            continue

        purpose_score, purpose_reason = _score_purpose(
            purpose, product.supported_purposes or []
        )
        if purpose_score == 0:
            continue

        age_score, age_reason = _score_business_age(
            business_age_months, product.min_business_age_months
        )
        if age_score == 0:
            continue

        try:
            calc = calculate_credit(
                amount=requested_amount,
                annual_rate=product.interest_rate,
                term_months=term_months,
            )
            monthly_payment = calc["monthly_payment"]
        except ValueError:
            continue

        income_score, income_reason = _score_income(
            monthly_payment, monthly_revenue
        )

        total_score = (
            amount_score * Decimal("0.40")
            + term_score * Decimal("0.30")
            + income_score * Decimal("0.20")
            + age_score * Decimal("0.10")
        ) * Decimal("100")

        reasons = [
            r
            for r in [
                amount_reason,
                term_reason,
                purpose_reason,
                age_reason,
                income_reason,
            ]
            if r
        ]

        results.append(
            {
                "product_id": product.id,
                "match_score": total_score.quantize(Decimal("0.01")),
                "estimated_monthly_payment": monthly_payment,
                "reasons": reasons,
            }
        )

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results
