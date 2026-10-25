"""Credit product database model."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.json_type import JSONType


class CreditProduct(Base):
    """Credit product offered by a bank."""

    __tablename__ = "credit_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    bank_name: Mapped[str] = mapped_column(String(150), nullable=False)

    interest_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False
    )

    min_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False
    )
    max_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False
    )

    min_term_months: Mapped[int] = mapped_column(Integer, nullable=False)
    max_term_months: Mapped[int] = mapped_column(Integer, nullable=False)

    commission_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True, default=None
    )
    commission_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2), nullable=True, default=None
    )

    additional_conditions: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    supported_purposes: Mapped[list[str]] = mapped_column(
        JSONType,
        nullable=False,
        default=list,
        server_default="[]",
    )

    min_business_age_months: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=None
    )

    requires_collateral: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    applications = relationship(
        "CreditApplication",
        back_populates="credit_product",
    )

    recommendation_items = relationship(
        "RecommendationItem",
        back_populates="product",
    )
