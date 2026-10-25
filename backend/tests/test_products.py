from decimal import Decimal

import pytest
from sqlalchemy import select

from app.models.credit_product import CreditProduct


@pytest.fixture(scope="function")
def seeded_client(client, TestingSessionLocal):
    db = TestingSessionLocal()
    db.add_all(
        [
            CreditProduct(
                name="Потребительский кредит",
                bank_name="Альфа-Банк",
                interest_rate=Decimal("19.90"),
                min_amount=Decimal("50000.00"),
                max_amount=Decimal("5000000.00"),
                min_term_months=6,
                max_term_months=60,
                commission_rate=Decimal("0.00"),
                commission_amount=Decimal("0.00"),
                additional_conditions="Тестовый продукт",
                is_active=True,
            ),
            CreditProduct(
                name="Неактивный продукт",
                bank_name="Альфа-Банк",
                interest_rate=Decimal("20.00"),
                min_amount=Decimal("10000.00"),
                max_amount=Decimal("100000.00"),
                min_term_months=3,
                max_term_months=12,
                is_active=False,
            ),
        ]
    )
    db.commit()
    db.close()
    return client


def test_get_products_returns_active_products(seeded_client):
    response = seeded_client.get("/api/v1/products")

    assert response.status_code == 200

    products = response.json()
    assert len(products) == 1
    assert products[0]["name"] == "Потребительский кредит"
    assert products[0]["bank_name"] == "Альфа-Банк"
    assert products[0]["interest_rate"] == "19.90"


def test_get_product_by_id(seeded_client):
    products_response = seeded_client.get("/api/v1/products")
    product_id = products_response.json()[0]["id"]

    response = seeded_client.get(f"/api/v1/products/{product_id}")

    assert response.status_code == 200
    assert response.json()["id"] == product_id
    assert response.json()["bank_name"] == "Альфа-Банк"


def test_get_missing_product_returns_404(seeded_client):
    response = seeded_client.get("/api/v1/products/999999")

    assert response.status_code == 404


def test_get_inactive_product_returns_404(seeded_client, TestingSessionLocal):
    active_product_id = seeded_client.get("/api/v1/products").json()[0]["id"]

    with TestingSessionLocal() as db:
        inactive_product = db.scalar(
            select(CreditProduct).where(CreditProduct.is_active.is_(False))
        )
        inactive_product_id = inactive_product.id

    assert inactive_product_id != active_product_id

    response = seeded_client.get(f"/api/v1/products/{inactive_product_id}")

    assert response.status_code == 404