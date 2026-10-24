
from decimal import Decimal

from pydantic import BaseModel, Field


class CreditCalculationRequest(BaseModel):
    product_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0)
    term_months: int = Field(gt=0)


class CreditCalculationResponse(BaseModel):
    product_id: int
    product_name: str
    bank_name: str
    interest_rate: Decimal
    amount: Decimal
    term_months: int
    monthly_payment: Decimal
    total_payment: Decimal
    overpayment: Decimal
    commission: Decimal


class CreditComparisonRequest(BaseModel):
    amount: Decimal = Field(gt=0)
    term_months: int = Field(gt=0)


class CreditComparisonResponse(BaseModel):
    amount: Decimal
    term_months: int
    products: list[CreditCalculationResponse]
