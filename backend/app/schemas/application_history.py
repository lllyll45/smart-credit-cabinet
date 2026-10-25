"""Pydantic schemas for application history."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ApplicationHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    application_id: int
    old_status: str | None
    new_status: str
    comment: str | None
    created_at: datetime
