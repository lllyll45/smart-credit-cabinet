"""Credit application database model."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CreditApplication(Base):
    __tablename__ = "credit_applications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    credit_product_id: Mapped[int | None] = mapped_column(
        ForeignKey("credit_products.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    term_months: Mapped[int] = mapped_column(nullable=False)

    purpose: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Financial information about the business
    monthly_income: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    # Business borrower information
    organization_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    organization_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    inn: Mapped[str | None] = mapped_column(
        String(12),
        nullable=True,
    )

    # Legacy field retained for compatibility with existing applications
    employment: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="draft",
        server_default="draft",
    )

    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    decision_comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Algorithm assessment, separate from the final staff decision
    preliminary_result: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        default=None,
    )

    monthly_payment: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    total_payment: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    overpayment: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="applications",
    )

    credit_product = relationship(
        "CreditProduct",
        back_populates="applications",
    )

    history = relationship(
        "ApplicationHistory",
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="ApplicationHistory.created_at",
    )