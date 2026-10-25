"""Тесты подбора кредитных предложений."""

from decimal import Decimal

import pytest

from app.models.credit_product import CreditProduct


@pytest.fixture(scope="function")
def seeded_products(TestingSessionLocal):
    db = TestingSessionLocal()
    db.add_all(
        [
            CreditProduct(
                name="Оборотный",
                bank_name="Банк",
                interest_rate=Decimal("15.00"),
                min_amount=Decimal("50000"),
                max_amount=Decimal("1000000"),
                min_term_months=6,
                max_term_months=24,
                commission_rate=Decimal("0"),
                is_active=True,
                supported_purposes=["working_capital"],
                min_business_age_months=6,
            ),
            CreditProduct(
                name="Оборудование",
                bank_name="Банк",
                interest_rate=Decimal("18.00"),
                min_amount=Decimal("100000"),
                max_amount=Decimal("5000000"),
                min_term_months=12,
                max_term_months=60,
                commission_rate=Decimal("0"),
                is_active=True,
                supported_purposes=["equipment"],
                min_business_age_months=12,
            ),
            CreditProduct(
                name="Неактивный",
                bank_name="Банк",
                interest_rate=Decimal("10.00"),
                min_amount=Decimal("10000"),
                max_amount=Decimal("10000000"),
                min_term_months=1,
                max_term_months=120,
                is_active=False,
            ),
        ]
    )
    db.commit()
    db.close()


def test_create_recommendation_returns_matching(
    client, registered_user, seeded_products
):
    res = client.post(
        "/api/v1/recommendations",
        json={
            "requested_amount": "200000",
            "term_months": 18,
            "purpose": "working_capital",
            "monthly_revenue": "200000",
            "business_age_months": 24,
        },
        headers=registered_user["headers"],
    )
    assert res.status_code == 201
    data = res.json()
    assert data["requested_amount"] == "200000.00"
    assert data["term_months"] == 18
    assert data["purpose"] == "working_capital"
    assert len(data["items"]) >= 1
    first = data["items"][0]
    assert "match_score" in first
    assert "reasons" in first
    assert "estimated_monthly_payment" in first


def test_recommendation_filters_out_wrong_purpose(
    client, registered_user, seeded_products
):
    res = client.post(
        "/api/v1/recommendations",
        json={
            "requested_amount": "200000",
            "term_months": 18,
            "purpose": "equipment",
            "monthly_revenue": "200000",
            "business_age_months": 24,
        },
        headers=registered_user["headers"],
    )
    assert res.status_code == 201
    products = {item["product_id"] for item in res.json()["items"]}
    all_products = client.get("/api/v1/products").json()
    for p in all_products:
        if p["name"] == "Оборотный":
            assert p["id"] not in products


def test_recommendation_filters_out_wrong_amount(
    client, registered_user, seeded_products
):
    res = client.post(
        "/api/v1/recommendations",
        json={
            "requested_amount": "5000",
            "term_months": 12,
            "purpose": "working_capital",
        },
        headers=registered_user["headers"],
    )
    assert res.status_code == 201
    assert res.json()["items"] == []


def test_get_recommendation_by_id(
    client, registered_user, seeded_products
):
    created = client.post(
        "/api/v1/recommendations",
        json={
            "requested_amount": "200000",
            "term_months": 18,
            "purpose": "working_capital",
            "monthly_revenue": "200000",
            "business_age_months": 24,
        },
        headers=registered_user["headers"],
    )
    rec_id = created.json()["id"]

    res = client.get(
        f"/api/v1/recommendations/{rec_id}",
        headers=registered_user["headers"],
    )
    assert res.status_code == 200
    assert res.json()["id"] == rec_id


def test_get_recommendation_404_for_other_user(
    client, registered_user, second_user, seeded_products
):
    created = client.post(
        "/api/v1/recommendations",
        json={
            "requested_amount": "200000",
            "term_months": 18,
            "purpose": "working_capital",
        },
        headers=registered_user["headers"],
    )
    rec_id = created.json()["id"]

    res = client.get(
        f"/api/v1/recommendations/{rec_id}",
        headers=second_user["headers"],
    )
    assert res.status_code == 404


def test_recommendation_requires_auth(client):
    res = client.post(
        "/api/v1/recommendations",
        json={
            "requested_amount": "200000",
            "term_months": 18,
            "purpose": "working_capital",
        },
    )
    assert res.status_code == 401
