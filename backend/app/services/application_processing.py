
"""Credit application processing service."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.credit_application import CreditApplication
from app.models.credit_product import CreditProduct
from app.services.calculator import calculate_credit


def process_credit_application(
    db: Session,
    application: CreditApplication,
) -> CreditApplication:
    """Calculate payments and apply demo-only decision rules."""

    if application.status != "draft":
        raise ValueError("Only draft applications can be processed")

    if application.credit_product_id is None:
        raise ValueError("Select a credit product before processing")

    product = db.get(CreditProduct, application.credit_product_id)

    if product is None or not product.is_active:
        raise ValueError("Credit product is missing or inactive")

    if not product.min_amount <= application.amount <= product.max_amount:
        raise ValueError("Application amount is outside product limits")

    if not (
        product.min_term_months
        <= application.term_months
        <= product.max_term_months
    ):
        raise ValueError("Application term is outside product limits")

    if application.monthly_income is None or application.monthly_income <= 0:
        raise ValueError("Monthly income must be positive")

    calculation = calculate_credit(
        amount=application.amount,
        annual_rate=product.interest_rate,
        term_months=application.term_months,
    )

    monthly_payment = calculation["monthly_payment"]

    application.monthly_payment = monthly_payment
    application.total_payment = calculation["total_payment"]
    application.overpayment = calculation["overpayment"]

    payment_to_income = monthly_payment / application.monthly_income

    # Demonstration rule only, not a real bank scoring model.
    if payment_to_income <= Decimal("0.40"):
        application.status = "approved"
        application.decision_comment = (
            "Заявка одобрена по демонстрационным правилам: "
            "ежемесячный платёж не превышает 40% заявленного дохода."
        )
    else:
        application.status = "rejected"
        application.decision_comment = (
            "Заявка отклонена по демонстрационным правилам: "
            "ежемесячный платёж превышает 40% заявленного дохода."
        )

    db.commit()
    db.refresh(application)

    return application
