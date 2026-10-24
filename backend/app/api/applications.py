
"""Credit applications API."""

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.auth import CurrentUser
from app.core.database import get_db
from app.models.credit_application import CreditApplication
from app.models.credit_product import CreditProduct
from app.schemas.credit_application import (
    CreditApplicationCreate,
    CreditApplicationResponse,
    CreditApplicationUpdate,
)

router = APIRouter(
    prefix="/applications",
    tags=["Credit applications"],
)

DbSession = Annotated[Session, Depends(get_db)]


def validate_credit_product(
    db: Session,
    product_id: int,
    amount: Decimal,
    term_months: int,
) -> CreditProduct:
    """Check that a product is active and supports the requested loan."""

    product = db.scalar(
        select(CreditProduct).where(
            CreditProduct.id == product_id,
        )
    )

    if product is None or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Credit product does not exist or is inactive",
        )

    if not product.min_amount <= amount <= product.max_amount:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Amount is outside the credit product limits",
        )

    if not product.min_term_months <= term_months <= product.max_term_months:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Term is outside the credit product limits",
        )

    return product


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
    validate_credit_product(
        db=db,
        product_id=data.credit_product_id,
        amount=data.amount,
        term_months=data.term_months,
    )

    application = CreditApplication(
        **data.model_dump(),
        user_id=user.id,
        status="draft",
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return application


@router.get(
    "",
    response_model=list[CreditApplicationResponse],
)
def list_applications(
    user: CurrentUser,
    db: DbSession,
):
    query = (
        select(CreditApplication)
        .where(CreditApplication.user_id == user.id)
        .order_by(CreditApplication.created_at.desc())
    )

    return db.scalars(query).all()


@router.get(
    "/{application_id}",
    response_model=CreditApplicationResponse,
)
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

    if any(
        field in changes
        for field in ("credit_product_id", "amount", "term_months")
    ):
        product_id = changes.get(
            "credit_product_id",
            application.credit_product_id,
        )
        amount = changes.get("amount", application.amount)
        term_months = changes.get(
            "term_months",
            application.term_months,
        )

        if product_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Credit product must be selected",
            )

        validate_credit_product(
            db=db,
            product_id=product_id,
            amount=amount,
            term_months=term_months,
        )

    for field, value in changes.items():
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

    if application.credit_product_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Select a credit product before submitting",
        )

    validate_credit_product(
        db=db,
        product_id=application.credit_product_id,
        amount=application.amount,
        term_months=application.term_months,
    )

    application.status = "submitted"

    db.commit()
    db.refresh(application)

    return application
