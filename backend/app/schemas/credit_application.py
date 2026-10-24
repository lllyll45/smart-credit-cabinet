
"""Pydantic schemas for credit applications."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CreditApplicationCreate(BaseModel):
    credit_product_id: int = Field(gt=0)

    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    term_months: int = Field(gt=0, le=360)
    purpose: str = Field(min_length=3, max_length=255)
    monthly_income: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    employment: str = Field(min_length=2, max_length=100)

class CreditApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    credit_product_id: int | None

    amount: Decimal
    term_months: int
    purpose: str
    monthly_income: Decimal
    employment: str

    status: str
    comment: str | None

    created_at: datetime
    updated_at: datetime


class CreditApplicationUpdate(BaseModel):
    credit_product_id: int | None = Field(
        default=None,
        gt=0,
    )

    amount: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    term_months: int | None = Field(
        default=None,
        gt=0,
        le=360,
    )
    purpose: str | None = Field(
        default=None,
        min_length=3,
        max_length=255,
    )
    monthly_income: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    employment: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
