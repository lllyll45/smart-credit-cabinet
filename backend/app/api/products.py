
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.credit_product import CreditProduct
from app.schemas.credit_product import CreditProductResponse

router = APIRouter(prefix="/products", tags=["Credit products"])


@router.get("", response_model=list[CreditProductResponse])
def get_products(
    db: Session = Depends(get_db),
) -> list[CreditProduct]:
    statement = (
        select(CreditProduct)
        .where(CreditProduct.is_active.is_(True))
        .order_by(CreditProduct.id)
    )
    return list(db.scalars(statement).all())


@router.get(
    "/{product_id}",
    response_model=CreditProductResponse,
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> CreditProduct:
    product = db.get(CreditProduct, product_id)

    if product is None or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credit product not found",
        )

    return product
