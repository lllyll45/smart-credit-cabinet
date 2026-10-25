"""Pydantic schemas for business profile."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BusinessProfileUpsert(BaseModel):
    """Схема создания/обновления профиля бизнеса."""

    business_name: str = Field(min_length=1, max_length=255)
    legal_form: str = Field(pattern="^(IP|OOO)$")
    industry: str | None = Field(default=None, max_length=100)
    region: str | None = Field(default=None, max_length=100)
    business_start_date: date | None = None
    monthly_revenue: Decimal | None = Field(
        default=None, ge=0, max_digits=15, decimal_places=2
    )


class BusinessProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    business_name: str
    legal_form: str
    industry: str | None
    region: str | None
    business_start_date: date | None
    monthly_revenue: Decimal | None
    created_at: datetime
    updated_at: datetime
