
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CreditProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    bank_name: str
    interest_rate: Decimal = Field(ge=0, le=100)
    min_amount: Decimal
    max_amount: Decimal
    min_term_months: int
    max_term_months: int
    commission_rate: Decimal | None = None
    commission_amount: Decimal | None = None
    additional_conditions: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
