"""Schemas for staff credit application decisions."""

from pydantic import BaseModel, Field


class ApplicationRejection(BaseModel):
    reason: str = Field(min_length=3, max_length=1000)
