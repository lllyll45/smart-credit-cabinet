"""Service for recording application status changes."""

from sqlalchemy.orm import Session

from app.models.application_history import ApplicationHistory
from app.models.credit_application import CreditApplication


def record_status_change(
    db: Session,
    application: CreditApplication,
    old_status: str | None,
    new_status: str,
    comment: str | None = None,
) -> ApplicationHistory:
    """Записывает изменение статуса в историю (без commit)."""
    record = ApplicationHistory(
        application_id=application.id,
        old_status=old_status,
        new_status=new_status,
        comment=comment,
    )
    db.add(record)
    return record
