"""Recommendation database models."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.json_type import JSONType


class Recommendation(Base):
    """Результат подбора предложений для пользователя."""

    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    requested_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False
    )
    term_months: Mapped[int] = mapped_column(Integer, nullable=False)
    purpose: Mapped[str] = mapped_column(String(100), nullable=False)

    monthly_revenue: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    business_age_months: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    items = relationship(
        "RecommendationItem",
        back_populates="recommendation",
        cascade="all, delete-orphan",
        order_by="RecommendationItem.match_score.desc()",
    )


class RecommendationItem(Base):
    """Один продукт в результате подбора."""

    __tablename__ = "recommendation_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    recommendation_id: Mapped[int] = mapped_column(
        ForeignKey("recommendations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("credit_products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    match_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False
    )
    estimated_monthly_payment: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2), nullable=True
    )

    reasons: Mapped[list[str]] = mapped_column(
        JSONType,
        nullable=False,
        default=list,
        server_default="[]",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    recommendation = relationship("Recommendation", back_populates="items")
    product = relationship("CreditProduct", back_populates="recommendation_items")
