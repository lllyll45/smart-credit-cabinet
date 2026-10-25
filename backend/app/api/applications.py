"""Credit application API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.auth import CurrentUser, StaffUser
from app.core.database import get_db
from app.models.credit_application import CreditApplication
from app.models.credit_product import CreditProduct
from app.models.application_history import ApplicationHistory
from app.schemas.application_decision import ApplicationRejection
from app.schemas.credit_application import (
    CreditApplicationCreate,
    CreditApplicationResponse,
    CreditApplicationUpdate,
)
from app.services.application_processing import process_credit_application
from app.schemas.application_history import ApplicationHistoryResponse
from app.services.application_history import record_status_change


DbSession = Annotated[Session, Depends(get_db)]

router = APIRouter(
    prefix="/applications",
    tags=["Applications"],
)


def validate_credit_product(
    db: Session,
    product_id: int,
    amount,
    term_months: int,
) -> CreditProduct:
    """Validate product availability and its limits."""

    product = db.get(CreditProduct, product_id)

    if product is None or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Credit product not found or inactive",
        )

    if not product.min_amount <= amount <= product.max_amount:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Application amount is outside product limits",
        )

    if not (
        product.min_term_months
        <= term_months
        <= product.max_term_months
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Application term is outside product limits",
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
    """Create a draft credit application."""

    validate_credit_product(
        db=db,
        product_id=data.credit_product_id,
        amount=data.amount,
        term_months=data.term_months,
    )

    application = CreditApplication(
        user_id=user.id,
        credit_product_id=data.credit_product_id,
        amount=data.amount,
        term_months=data.term_months,
        purpose=data.purpose,
        monthly_income=data.monthly_income,
        employment=data.employment,
        status="draft",
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    record_status_change(
        db=db,
        application=application,
        old_status=None,
        new_status="draft",
        comment="Заявка создана",
    )
    db.commit()

    return application


@router.get(
    "",
    response_model=list[CreditApplicationResponse],
)
def list_applications(
    user: CurrentUser,
    db: DbSession,
):
    """Return applications belonging to the current user."""

    applications = db.scalars(
        select(CreditApplication)
        .where(CreditApplication.user_id == user.id)
        .order_by(CreditApplication.id.desc())
    ).all()

    return applications


@router.get(
    "/staff",
    response_model=list[CreditApplicationResponse],
)
def list_staff_applications(
    staff: StaffUser,
    db: DbSession,
):
    """Return all applications for bank staff."""

    return db.scalars(
        select(CreditApplication)
        .order_by(CreditApplication.id.desc())
    ).all()


@router.get(
    "/{application_id}",
    response_model=CreditApplicationResponse,
)
def get_application(
    application_id: int,
    user: CurrentUser,
    db: DbSession,
):
    """Return a specific application belonging to the current user."""

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


@router.get(
    "/{application_id}/history",
    response_model=list[ApplicationHistoryResponse],
)
def get_application_history(
    application_id: int,
    user: CurrentUser,
    db: DbSession,
):
    """Возвращает историю изменения статусов заявки текущего пользователя."""

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

    history = db.scalars(
        select(ApplicationHistory)
        .where(ApplicationHistory.application_id == application_id)
        .order_by(ApplicationHistory.created_at)
    ).all()

    return list(history)


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
    """Update an application while it is a draft."""

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
            detail="Only draft applications can be updated",
        )

    update_data = data.model_dump(exclude_unset=True)

    new_product_id = update_data.get(
        "credit_product_id",
        application.credit_product_id,
    )
    new_amount = update_data.get("amount", application.amount)
    new_term_months = update_data.get(
        "term_months",
        application.term_months,
    )

    if new_product_id is not None:
        validate_credit_product(
            db=db,
            product_id=new_product_id,
            amount=new_amount,
            term_months=new_term_months,
        )

    for field, value in update_data.items():
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
    """Calculate payments and submit the application for staff review."""

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
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Select a credit product before submitting",
        )

    validate_credit_product(
        db=db,
        product_id=application.credit_product_id,
        amount=application.amount,
        term_months=application.term_months,
    )

    old_status = application.status

    try:
        application = process_credit_application(
            db=db,
            application=application,
        )
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    record_status_change(
        db=db,
        application=application,
        old_status=old_status,
        new_status=application.status,
        comment="Заявка отправлена на рассмотрение",
    )
    db.commit()
    db.refresh(application)

    return application


@router.post(
    "/{application_id}/approve",
    response_model=CreditApplicationResponse,
)
def approve_application(
    application_id: int,
    staff: StaffUser,
    db: DbSession,
):
    """Approve an application submitted for staff review."""

    application = db.get(CreditApplication, application_id)

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    if application.status != "submitted":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only submitted applications can be approved",
        )

    old_status = application.status
    application.status = "approved"
    application.decision_comment = "Заявка одобрена сотрудником банка."

    record_status_change(
        db=db,
        application=application,
        old_status=old_status,
        new_status="approved",
        comment="Заявка одобрена сотрудником банка",
    )

    db.commit()
    db.refresh(application)

    return application


@router.post(
    "/{application_id}/reject",
    response_model=CreditApplicationResponse,
)
def reject_application(
    application_id: int,
    data: ApplicationRejection,
    staff: StaffUser,
    db: DbSession,
):
    """Reject an application with a reason provided by staff."""

    application = db.get(CreditApplication, application_id)

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    if application.status != "submitted":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only submitted applications can be rejected",
        )

    reason = data.reason.strip()

    if len(reason) < 3:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Rejection reason must contain at least 3 characters",
        )

    old_status = application.status
    application.status = "rejected"
    application.decision_comment = reason

    record_status_change(
        db=db,
        application=application,
        old_status=old_status,
        new_status="rejected",
        comment=f"Заявка отклонена: {reason}",
    )

    db.commit()
    db.refresh(application)

    return application