"""Business profile API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.auth import CurrentUser
from app.core.database import get_db
from app.models.business_profile import BusinessProfile
from app.schemas.business_profile import (
    BusinessProfileResponse,
    BusinessProfileUpsert,
)


DbSession = Annotated[Session, Depends(get_db)]

router = APIRouter(
    prefix="/business-profile",
    tags=["Business profile"],
)


@router.get("", response_model=BusinessProfileResponse)
def get_business_profile(user: CurrentUser, db: DbSession):
    """Возвращает профиль бизнеса текущего пользователя."""
    profile = db.scalar(
        select(BusinessProfile).where(BusinessProfile.user_id == user.id)
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found",
        )

    return profile


@router.put("", response_model=BusinessProfileResponse)
def upsert_business_profile(
    data: BusinessProfileUpsert,
    user: CurrentUser,
    db: DbSession,
):
    """Создаёт или полностью обновляет профиль бизнеса пользователя."""
    profile = db.scalar(
        select(BusinessProfile).where(BusinessProfile.user_id == user.id)
    )

    if profile is None:
        profile = BusinessProfile(
            user_id=user.id,
            business_name=data.business_name,
            legal_form=data.legal_form,
            industry=data.industry,
            region=data.region,
            business_start_date=data.business_start_date,
            monthly_revenue=data.monthly_revenue,
        )
        db.add(profile)
    else:
        profile.business_name = data.business_name
        profile.legal_form = data.legal_form
        profile.industry = data.industry
        profile.region = data.region
        profile.business_start_date = data.business_start_date
        profile.monthly_revenue = data.monthly_revenue

    db.commit()
    db.refresh(profile)

    return profile
