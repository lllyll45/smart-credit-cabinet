"""Recommendation API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.auth import CurrentUser
from app.core.database import get_db
from app.models.recommendation import Recommendation, RecommendationItem
from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
)
from app.services.recommendation import build_recommendations


DbSession = Annotated[Session, Depends(get_db)]

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


@router.post(
    "",
    response_model=RecommendationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_recommendation(
    data: RecommendationRequest,
    user: CurrentUser,
    db: DbSession,
):
    """Подбирает продукты и сохраняет результат для текущего пользователя."""

    scored = build_recommendations(
        db=db,
        requested_amount=data.requested_amount,
        term_months=data.term_months,
        purpose=data.purpose,
        monthly_revenue=data.monthly_revenue,
        business_age_months=data.business_age_months,
    )

    recommendation = Recommendation(
        user_id=user.id,
        requested_amount=data.requested_amount,
        term_months=data.term_months,
        purpose=data.purpose,
        monthly_revenue=data.monthly_revenue,
        business_age_months=data.business_age_months,
    )
    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)

    for item in scored:
        db.add(
            RecommendationItem(
                recommendation_id=recommendation.id,
                product_id=item["product_id"],
                match_score=item["match_score"],
                estimated_monthly_payment=item["estimated_monthly_payment"],
                reasons=item["reasons"],
            )
        )
    db.commit()
    db.refresh(recommendation)

    return recommendation


@router.get(
    "/{recommendation_id}",
    response_model=RecommendationResponse,
)
def get_recommendation(
    recommendation_id: int,
    user: CurrentUser,
    db: DbSession,
):
    """Возвращает сохранённый результат подбора текущего пользователя."""

    recommendation = db.scalar(
        select(Recommendation).where(
            Recommendation.id == recommendation_id,
            Recommendation.user_id == user.id,
        )
    )

    if recommendation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found",
        )

    return recommendation
