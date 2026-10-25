from decimal import Decimal

import pytest

from app.models.credit_product import CreditProduct


@pytest.fixture(scope="function")
def seeded_client(client, TestingSessionLocal):
    """Наполняет общую тестовую БД продуктами и возвращает client."""
    db = TestingSessionLocal()
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
    db.close()
    return client


def test_calculate_credit_returns_result(seeded_client):
    client = seeded_client
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


def test_calculate_missing_product_returns_404(seeded_client):
    response = seeded_client.post(
        "/api/v1/calculator/calculate",
        json={
            "product_id": 999999,
            "amount": "120000",
            "term_months": 12,
        },
    )

    assert response.status_code == 404


def test_calculate_inactive_product_returns_404(seeded_client, TestingSessionLocal):
    with TestingSessionLocal() as db:
        inactive_product = db.query(CreditProduct).filter_by(is_active=False).first()
        product_id = inactive_product.id

    response = seeded_client.post(
        "/api/v1/calculator/calculate",
        json={
            "product_id": product_id,
            "amount": "120000",
            "term_months": 12,
        },
    )

    assert response.status_code == 404


def test_calculate_out_of_range_amount_returns_422(seeded_client):
    product_id = seeded_client.get("/api/v1/products").json()[0]["id"]

    response = seeded_client.post(
        "/api/v1/calculator/calculate",
        json={
            "product_id": product_id,
            "amount": "1000000",
            "term_months": 12,
        },
    )

    assert response.status_code == 422


def test_compare_returns_products_sorted_by_total_payment(seeded_client):
    response = seeded_client.post(
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


def test_compare_excludes_products_outside_limits(seeded_client):
    response = seeded_client.post(
        "/api/v1/calculator/compare",
        json={
            "amount": "900000",
            "term_months": 12,
        },
    )

    assert response.status_code == 200
    assert response.json()["products"] == []


def test_calculator_rejects_invalid_request(seeded_client):
    response = seeded_client.post(
        "/api/v1/calculator/calculate",
        json={
            "product_id": 1,
            "amount": "-100",
            "term_months": 12,
        },
    )

    assert response.status_code == 422


def test_calculate_with_fixed_commission_amount(seeded_client, TestingSessionLocal):
    """Проверяет ветку commission_amount (фиксированная сумма, не %)."""
    db = TestingSessionLocal()
    product = CreditProduct(
        name="С фикс. комиссией",
        bank_name="Банк",
        interest_rate=Decimal("15.00"),
        min_amount=Decimal("10000.00"),
        max_amount=Decimal("1000000.00"),
        min_term_months=6,
        max_term_months=36,
        commission_rate=None,
        commission_amount=Decimal("5000.00"),
        is_active=True,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    product_id = product.id
    db.close()

    res = seeded_client.post(
        "/api/v1/calculator/calculate",
        json={
            "product_id": product_id,
            "amount": "120000",
            "term_months": 12,
        },
    )
    assert res.status_code == 200
    assert res.json()["commission"] == "5000.00"


def test_calculate_disclaimer_present(seeded_client):
    """В ответе должно быть поле disclaimer (расчёт предварительный)."""
    products = seeded_client.get("/api/v1/products").json()
    product_id = products[0]["id"]

    res = seeded_client.post(
        "/api/v1/calculator/calculate",
        json={
            "product_id": product_id,
            "amount": "120000",
            "term_months": 12,
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "disclaimer" in data
    assert isinstance(data["disclaimer"], str)
    assert len(data["disclaimer"]) > 0