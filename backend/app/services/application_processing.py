
"""Credit application processing service."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.credit_application import CreditApplication
from app.models.credit_product import CreditProduct
from app.services.calculator import calculate_credit


MAX_PAYMENT_TO_INCOME_RATIO = Decimal("0.40")


def process_credit_application(
    db: Session,
    application: CreditApplication,
) -> CreditApplication:
    """Calculate payments and preliminary assessment for staff review."""

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

    monthly_payment = Decimal(str(calculation["monthly_payment"]))

    application.monthly_payment = monthly_payment
    application.total_payment = calculation["total_payment"]
    application.overpayment = calculation["overpayment"]

    payment_ratio = monthly_payment / application.monthly_income

    if payment_ratio <= MAX_PAYMENT_TO_INCOME_RATIO:
        application.preliminary_result = "likely_eligible"
    else:
        application.preliminary_result = "high_debt_burden"

    print("APPLICATION ID:", application.id)
    print("PAYMENT RATIO:", payment_ratio)
    print("PRELIMINARY RESULT:", application.preliminary_result)

    application.status = "submitted"
    application.decision_comment = None

    db.commit()
    db.refresh(application)

    return application