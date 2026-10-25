"""Юнит-тесты на process_credit_application."""

from decimal import Decimal

import pytest

from app.models.credit_application import CreditApplication
from app.models.credit_product import CreditProduct
from app.services.application_processing import process_credit_application


def _make_application(db, user_id, product_id, income):
    app = CreditApplication(
        user_id=user_id,
        credit_product_id=product_id,
        amount=Decimal("100000"),
        term_months=12,
        purpose="Тест",
        monthly_income=Decimal(income),
        employment="ИП",
        status="draft",
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


@pytest.fixture
def setup(db_engine, TestingSessionLocal, user_a_id):
    db = TestingSessionLocal()
    product = CreditProduct(
        name="P",
        bank_name="B",
        interest_rate=Decimal("12.00"),
        min_amount=Decimal("10000"),
        max_amount=Decimal("1000000"),
        min_term_months=6,
        max_term_months=36,
        is_active=True,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    yield db, product.id
    db.close()


def test_processing_approved(setup, user_a_id):
    db, product_id = setup
    app = _make_application(db, user_a_id, product_id, "50000")
    result = process_credit_application(db, app)
    assert result.status == "approved"
    assert result.monthly_payment is not None


def test_processing_rejected(setup, user_a_id):
    db, product_id = setup
    app = _make_application(db, user_a_id, product_id, "5000")
    result = process_credit_application(db, app)
    assert result.status == "rejected"


def test_processing_raises_on_non_draft(setup, user_a_id):
    db, product_id = setup
    app = _make_application(db, user_a_id, product_id, "50000")
    app.status = "submitted"
    db.commit()
    with pytest.raises(ValueError):
        process_credit_application(db, app)


def test_processing_raises_on_missing_income(setup, user_a_id):
    db, product_id = setup
    app = _make_application(db, user_a_id, product_id, "50000")
    app.monthly_income = None
    db.commit()
    with pytest.raises(ValueError):
        process_credit_application(db, app)