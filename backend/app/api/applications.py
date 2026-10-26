"""Credit application API endpoints."""

from typing import Annotated
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.auth import CurrentUser, StaffUser
from app.core.database import get_db
from app.models.application_history import ApplicationHistory
from app.models.business_profile import BusinessProfile
from app.models.credit_application import CreditApplication
from app.models.credit_product import CreditProduct
from app.schemas.application_decision import ApplicationRejection
from app.schemas.application_history import ApplicationHistoryResponse
from app.schemas.credit_application import (
    CreditApplicationCreate,
    CreditApplicationResponse,
    CreditApplicationUpdate,
)
from app.services.application_history import record_status_change
from app.services.application_processing import process_credit_application


DbSession = Annotated[Session, Depends(get_db)]

router = APIRouter(
    prefix="/applications",
    tags=["Applications"],
)


def validate_credit_product(
    db: Session,
    product_id: int,
    amount: Decimal,
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


def get_application_or_404(
    db: Session,
    application_id: int,
) -> CreditApplication:
    """Return an application or raise 404."""

    application = db.get(CreditApplication, application_id)

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    return application


def check_application_access(
    application: CreditApplication,
    user: CurrentUser,
) -> None:
    """Allow staff/admin to view any application, clients only their own."""

    if user.role not in ("staff", "admin"):
        if application.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )


def serialize_application(
    db: Session,
    application: CreditApplication,
) -> dict:
    """Serialize application and add its owner's business profile."""

    result = CreditApplicationResponse.model_validate(
        application
    ).model_dump()

    business_profile = db.scalar(
        select(BusinessProfile).where(
            BusinessProfile.user_id == application.user_id
        )
    )

    result.update(
        {
            "business_name": (
                business_profile.business_name
                if business_profile else None
            ),
            "legal_form": (
                business_profile.legal_form
                if business_profile else None
            ),
            "industry": (
                business_profile.industry
                if business_profile else None
            ),
            "region": (
                business_profile.region
                if business_profile else None
            ),
            "business_start_date": (
                business_profile.business_start_date
                if business_profile else None
            ),
        }
    )

    return result


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
    """Create a draft application using the user's business profile."""

    validate_credit_product(
        db=db,
        product_id=data.credit_product_id,
        amount=data.amount,
        term_months=data.term_months,
    )

    business_profile = db.scalar(
        select(BusinessProfile).where(
            BusinessProfile.user_id == user.id,
        )
    )

    if business_profile is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Create a business profile before applying for credit",
        )

    if business_profile.monthly_revenue is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Specify monthly revenue in your business profile",
        )

    application = CreditApplication(
        user_id=user.id,
        credit_product_id=data.credit_product_id,
        amount=data.amount,
        term_months=data.term_months,
        purpose=data.purpose,
        monthly_income=business_profile.monthly_revenue,
        employment=None,
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
    db.refresh(application)

    return serialize_application(db, application)


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

    return [
        serialize_application(db, application)
        for application in applications
    ]


@router.get(
    "/staff",
    response_model=list[CreditApplicationResponse],
)
def list_staff_applications(
    staff: StaffUser,
    db: DbSession,
):
    """Return all applications for bank staff."""

    applications = db.scalars(
        select(CreditApplication)
        .order_by(CreditApplication.id.desc())
    ).all()

    return [
        serialize_application(db, application)
        for application in applications
    ]


@router.get(
    "/{application_id}",
    response_model=CreditApplicationResponse,
)
def get_application(
    application_id: int,
    user: CurrentUser,
    db: DbSession,
):
    """Return application details and the owner's business profile."""

    application = get_application_or_404(db, application_id)
    check_application_access(application, user)

    return serialize_application(db, application)


@router.get(
    "/{application_id}/history",
    response_model=list[ApplicationHistoryResponse],
)
def get_application_history(
    application_id: int,
    user: CurrentUser,
    db: DbSession,
):
    """Return status history for an application."""

    application = get_application_or_404(db, application_id)
    check_application_access(application, user)

    history = db.scalars(
        select(ApplicationHistory)
        .where(
            ApplicationHistory.application_id == application_id
        )
        .order_by(ApplicationHistory.created_at.desc())
    ).all()

    return history


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

    return serialize_application(db, application)


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

    return serialize_application(db, application)


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

    application = get_application_or_404(db, application_id)

    if application.status not in ("submitted", "checking"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only submitted or checking applications can be approved",
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

    return serialize_application(db, application)


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

    application = get_application_or_404(db, application_id)

    if application.status not in ("submitted", "checking"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only submitted or checking applications can be rejected",
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

    return serialize_application(db, application)


@router.post(
    "/{application_id}/check",
    response_model=CreditApplicationResponse,
)
def start_checking(
    application_id: int,
    staff: StaffUser,
    db: DbSession,
):
    """Move an application to checking status."""

    application = get_application_or_404(db, application_id)

    if application.status != "submitted":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only submitted applications can be moved to checking",
        )

    old_status = application.status
    application.status = "checking"

    record_status_change(
        db=db,
        application=application,
        old_status=old_status,
        new_status="checking",
        comment="Заявка передана на проверку",
    )

    db.commit()
    db.refresh(application)

    return serialize_application(db, application)


@router.post(
    "/{application_id}/request-info",
    response_model=CreditApplicationResponse,
)
def request_more_info(
    application_id: int,
    staff: StaffUser,
    db: DbSession,
):
    """Request additional information from the applicant."""

    application = get_application_or_404(db, application_id)

    if application.status not in ("submitted", "checking"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only submitted or checking applications can request more info",
        )

    old_status = application.status
    application.status = "needs_info"
    application.decision_comment = "Требуется дополнительная информация."

    record_status_change(
        db=db,
        application=application,
        old_status=old_status,
        new_status="needs_info",
        comment="Запрошена дополнительная информация",
    )

    db.commit()
    db.refresh(application)

    return serialize_application(db, application)


@router.post(
    "/{application_id}/offer-alternative",
    response_model=CreditApplicationResponse,
)
def offer_alternative(
    application_id: int,
    staff: StaffUser,
    db: DbSession,
):
    """Offer alternative credit terms."""

    application = get_application_or_404(db, application_id)

    if application.status not in ("submitted", "checking"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only submitted or checking applications can offer alternative",
        )

    old_status = application.status
    application.status = "alternative_offer"
    application.decision_comment = (
        "Предложены альтернативные условия. "
        "Сотрудник банка свяжется с вами."
    )

    record_status_change(
        db=db,
        application=application,
        old_status=old_status,
        new_status="alternative_offer",
        comment="Предложены альтернативные условия",
    )

    db.commit()
    db.refresh(application)

    return serialize_application(db, application)
