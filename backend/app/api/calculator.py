
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.credit_product import CreditProduct
from app.schemas.calculator import (
    CreditCalculationRequest,
    CreditCalculationResponse,
    CreditComparisonRequest,
    CreditComparisonResponse,
)
from app.services.calculator import calculate_credit, money


router = APIRouter(prefix="/calculator", tags=["Credit calculator"])


def build_calculation(
    product: CreditProduct,
    amount: Decimal,
    term_months: int,
) -> CreditCalculationResponse:
    if not (
        product.min_amount <= amount <= product.max_amount
        and product.min_term_months <= term_months <= product.max_term_months
    ):
        raise HTTPException(
            status_code=422,
            detail="Сумма или срок не соответствуют условиям кредитного продукта",
        )

    result = calculate_credit(
        amount=amount,
        annual_rate=product.interest_rate,
        term_months=term_months,
    )

    if product.commission_rate is not None:
        commission = money(
            amount * product.commission_rate / Decimal("100")
        )
    elif product.commission_amount is not None:
        commission = money(product.commission_amount)
    else:
        commission = Decimal("0.00")

    return CreditCalculationResponse(
        product_id=product.id,
        product_name=product.name,
        bank_name=product.bank_name,
        interest_rate=product.interest_rate,
        amount=amount,
        term_months=term_months,
        monthly_payment=result["monthly_payment"],
        total_payment=money(result["total_payment"] + commission),
        overpayment=money(result["overpayment"] + commission),
        commission=commission,
    )


@router.post("/calculate", response_model=CreditCalculationResponse)
def calculate_product(
    request: CreditCalculationRequest,
    db: Session = Depends(get_db),
) -> CreditCalculationResponse:
    product = db.get(CreditProduct, request.product_id)

    if product is None or not product.is_active:
        raise HTTPException(status_code=404, detail="Кредитный продукт не найден")

    return build_calculation(product, request.amount, request.term_months)


@router.post("/compare", response_model=CreditComparisonResponse)
def compare_products(
    request: CreditComparisonRequest,
    db: Session = Depends(get_db),
) -> CreditComparisonResponse:
    statement = (
        select(CreditProduct)
        .where(CreditProduct.is_active.is_(True))
        .order_by(CreditProduct.id)
    )
    products = db.scalars(statement).all()
    results = []

    for product in products:
        if (
            product.min_amount <= request.amount <= product.max_amount
            and product.min_term_months
            <= request.term_months
            <= product.max_term_months
        ):
            results.append(
                build_calculation(product, request.amount, request.term_months)
            )

    results.sort(key=lambda item: item.total_payment)

    return CreditComparisonResponse(
        amount=request.amount,
        term_months=request.term_months,
        products=results,
    )
