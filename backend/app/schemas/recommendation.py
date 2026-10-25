"""Pydantic schemas for recommendations."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class RecommendationRequest(BaseModel):
    requested_amount: Decimal = Field(gt=0, max_digits=15, decimal_places=2)
    term_months: int = Field(gt=0, le=360)
    purpose: str = Field(min_length=1, max_length=100)
    monthly_revenue: Decimal | None = Field(
        default=None, gt=0, max_digits=15, decimal_places=2
    )
    business_age_months: int | None = Field(default=None, ge=0)


class RecommendationItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    match_score: Decimal
    estimated_monthly_payment: Decimal | None
    reasons: list[str]


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    requested_amount: Decimal
    term_months: int
    purpose: str
    monthly_revenue: Decimal | None
    business_age_months: int | None
    created_at: datetime
    items: list[RecommendationItemResponse]
