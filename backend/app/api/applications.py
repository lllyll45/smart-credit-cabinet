
"""Credit applications API."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.auth import CurrentUser
from app.core.database import get_db
from app.models.credit_application import CreditApplication
from app.schemas.credit_application import (
    CreditApplicationCreate,
    CreditApplicationResponse,
    CreditApplicationUpdate,
)
from fastapi import APIRouter

router = APIRouter(
    prefix="/applications",
    tags=["Credit applications"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=CreditApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_application(
    data: CreditApplicationCreate,
    user: CurrentUser,
    db: DbSession,
):
    application = CreditApplication(
        **data.model_dump(),
        user_id=user.id,
        status="draft",
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("", response_model=list[CreditApplicationResponse])
def list_applications(user: CurrentUser, db: DbSession):
    query = (
        select(CreditApplication)
        .where(CreditApplication.user_id == user.id)
        .order_by(CreditApplication.created_at.desc())
    )
    return db.scalars(query).all()


@router.get("/{application_id}", response_model=CreditApplicationResponse)
def get_application(
    application_id: int,
    user: CurrentUser,
    db: DbSession,
):
    application = db.scalar(
        select(CreditApplication).where(
            CreditApplication.id == application_id,
            CreditApplication.user_id == user.id,
        )
    )
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    return application


@router.patch(
    "/{application_id}",
    response_model=CreditApplicationResponse,
)
def update_application(
    application_id: int,
    data: CreditApplicationUpdate,
    user: CurrentUser,
    db: DbSession,
):
    application = db.scalar(
        select(CreditApplication).where(
            CreditApplication.id == application_id,
            CreditApplication.user_id == user.id,
        )
    )
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    if application.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft applications can be edited",
        )

    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        if value is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field} cannot be null",
            )
        setattr(application, field, value)

    db.commit()
    db.refresh(application)
    return application


@router.post(
    "/{application_id}/submit",
    response_model=CreditApplicationResponse,
)
def submit_application(
    application_id: int,
    user: CurrentUser,
    db: DbSession,
):
    application = db.scalar(
        select(CreditApplication).where(
            CreditApplication.id == application_id,
            CreditApplication.user_id == user.id,
        )
    )
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    if application.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft applications can be submitted",
        )

    application.status = "submitted"
    db.commit()
    db.refresh(application)
    return application
