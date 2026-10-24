
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.credit_product import CreditProduct


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        bind=engine,
        class_=Session,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        with TestingSessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestingSessionLocal() as db:
        db.add_all(
            [
                CreditProduct(
                    name="Кредит А",
                    bank_name="Тестовый банк",
                    interest_rate=Decimal("12.00"),
                    min_amount=Decimal("10000.00"),
                    max_amount=Decimal("500000.00"),
                    min_term_months=6,
                    max_term_months=60,
                    commission_rate=Decimal("0.00"),
                    commission_amount=Decimal("0.00"),
                    is_active=True,
                ),
                CreditProduct(
                    name="Кредит Б",
                    bank_name="Тестовый банк",
                    interest_rate=Decimal("20.00"),
                    min_amount=Decimal("10000.00"),
                    max_amount=Decimal("500000.00"),
                    min_term_months=6,
                    max_term_months=60,
                    commission_rate=Decimal("1.00"),
                    commission_amount=None,
                    is_active=True,
                ),
                CreditProduct(
                    name="Неактивный кредит",
                    bank_name="Тестовый банк",
                    interest_rate=Decimal("10.00"),
                    min_amount=Decimal("10000.00"),
                    max_amount=Decimal("500000.00"),
                    min_term_months=6,
                    max_term_months=60,
                    is_active=False,
                ),
            ]
        )
        db.commit()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_calculate_credit_returns_result(client):
    products = client.get("/api/v1/products").json()
    product_id = products[0]["id"]

    response = client.post(
        "/api/v1/calculator/calculate",
        json={
            "product_id": product_id,
            "amount": "120000",
            "term_months": 12,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["product_id"] == product_id
    assert data["product_name"] == "Кредит А"
    assert data["interest_rate"] == "12.00"
    assert data["monthly_payment"] == "10661.85"
    assert data["total_payment"] == "127942.20"
    assert data["overpayment"] == "7942.20"
    assert data["commission"] == "0.00"


def test_calculate_missing_product_returns_404(client):
    response = client.post(
        "/api/v1/calculator/calculate",
        json={
            "product_id": 999999,
            "amount": "120000",
            "term_months": 12,
        },
    )

    assert response.status_code == 404


def test_calculate_inactive_product_returns_404(client):
    # Находим неактивный продукт в тестовой базе через API его получить нельзя,
    # поэтому используем известный порядок добавления записей.
    with next(app.dependency_overrides[get_db]()) as db:
        inactive_product = db.query(CreditProduct).filter_by(
            is_active=False
        ).first()
        product_id = inactive_product.id

    response = client.post(
        "/api/v1/calculator/calculate",
        json={
            "product_id": product_id,
            "amount": "120000",
            "term_months": 12,
        },
    )

    assert response.status_code == 404


def test_calculate_out_of_range_amount_returns_422(client):
    product_id = client.get("/api/v1/products").json()[0]["id"]

    response = client.post(
        "/api/v1/calculator/calculate",
        json={
            "product_id": product_id,
            "amount": "1000000",
            "term_months": 12,
        },
    )

    assert response.status_code == 422


def test_compare_returns_products_sorted_by_total_payment(client):
    response = client.post(
        "/api/v1/calculator/compare",
        json={
            "amount": "120000",
            "term_months": 12,
        },
    )

    assert response.status_code == 200

    data = response.json()
    products = data["products"]

    assert len(products) == 2
    assert products[0]["total_payment"] < products[1]["total_payment"]
    assert products[0]["product_name"] == "Кредит А"


def test_compare_excludes_products_outside_limits(client):
    response = client.post(
        "/api/v1/calculator/compare",
        json={
            "amount": "900000",
            "term_months": 12,
        },
    )

    assert response.status_code == 200
    assert response.json()["products"] == []


def test_calculator_rejects_invalid_request(client):
    response = client.post(
        "/api/v1/calculator/calculate",
        json={
            "product_id": 1,
            "amount": "-100",
            "term_months": 12,
        },
    )

    assert response.status_code == 422
