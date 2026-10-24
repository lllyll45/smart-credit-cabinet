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
from app.services.application_processing import process_credit_application


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
    """Проверяет доступность кредитного продукта и его ограничения."""

    product = db.get(CreditProduct, product_id)

    if product is None or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Credit product not found or inactive",
        )

    if not product.min_amount <= amount <= product.max_amount:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Application amount is outside product limits",
        )

    if not (
        product.min_term_months
        <= term_months
        <= product.max_term_months
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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
    """Создаёт черновик кредитной заявки."""

    if data.credit_product_id is not None:
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

    return application


@router.get(
    "",
    response_model=list[CreditApplicationResponse],
)
def list_applications(
    user: CurrentUser,
    db: DbSession,
):
    """Возвращает заявки текущего пользователя."""

    applications = db.scalars(
        select(CreditApplication)
        .where(CreditApplication.user_id == user.id)
        .order_by(CreditApplication.id.desc())
    ).all()

    return applications


@router.get(
    "/{application_id}",
    response_model=CreditApplicationResponse,
)
def get_application(
    application_id: int,
    user: CurrentUser,
    db: DbSession,
):
    """Возвращает конкретную заявку текущего пользователя."""

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
    """Изменяет заявку, пока она находится в статусе черновика."""

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
    """Отправляет заявку и автоматически рассчитывает решение."""

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

    try:
        application = process_credit_application(
            db=db,
            application=application,
        )
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return application