"""Application history model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ApplicationHistory(Base):
    """Запись истории изменения статуса кредитной заявки."""

    __tablename__ = "application_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    application_id: Mapped[int] = mapped_column(
        ForeignKey("credit_applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    old_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    new_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    application = relationship(
        "CreditApplication",
        back_populates="history",
    )
