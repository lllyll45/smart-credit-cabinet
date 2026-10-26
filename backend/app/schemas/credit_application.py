"""Pydantic schemas for credit applications."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CreditApplicationCreate(BaseModel):
    credit_product_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    term_months: int = Field(gt=0, le=360)
    purpose: str = Field(min_length=3, max_length=255)


class CreditApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    credit_product_id: int | None
    amount: Decimal
    term_months: int
    purpose: str
    monthly_income: Decimal | None
    employment: str | None
    status: str
    comment: str | None
    decision_comment: str | None
    preliminary_result: str | None = None
    monthly_payment: Decimal | None
    total_payment: Decimal | None
    overpayment: Decimal | None
    created_at: datetime
    updated_at: datetime

    # Данные бизнес-профиля владельца заявки.
    business_name: str | None = None
    legal_form: str | None = None
    industry: str | None = None
    region: str | None = None
    business_start_date: date | None = None


class CreditApplicationUpdate(BaseModel):
    credit_product_id: int | None = Field(default=None, gt=0)
    amount: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    term_months: int | None = Field(default=None, gt=0, le=360)
    purpose: str | None = Field(
        default=None,
        min_length=3,
        max_length=255,
    )
