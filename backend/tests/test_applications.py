"""Тесты CRUD и submit кредитных заявок."""

import pytest
from sqlalchemy import select

from app.models.credit_product import CreditProduct


# ---------- СОЗДАНИЕ ----------

def test_create_application_success(client, registered_user, product_id):
    res = client.post(
        "/api/v1/applications",
        json={
            "credit_product_id": product_id,
            "amount": "100000",
            "term_months": 12,
            "purpose": "Тестовая цель",
            "monthly_income": "50000",
            "employment": "ИП",
        },
        headers=registered_user["headers"],
    )
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "draft"
    assert data["credit_product_id"] == product_id
    assert data["user_id"] == registered_user["user"]["id"]


def test_create_with_missing_product(client, registered_user):
    res = client.post(
        "/api/v1/applications",
        json={
            "credit_product_id": 999999,
            "amount": "100000",
            "term_months": 12,
            "purpose": "Тест",
            "monthly_income": "50000",
            "employment": "ИП",
        },
        headers=registered_user["headers"],
    )
    assert res.status_code == 422


def test_create_with_inactive_product(
    client, registered_user, TestingSessionLocal
):
    db = TestingSessionLocal()
    inactive = CreditProduct(
        name="Неактивный",
        bank_name="Банк",
        interest_rate=15.0,
        min_amount=10000,
        max_amount=1000000,
        min_term_months=6,
        max_term_months=36,
        is_active=False,
    )
    db.add(inactive)
    db.commit()
    db.refresh(inactive)
    pid = inactive.id
    db.close()

    res = client.post(
        "/api/v1/applications",
        json={
            "credit_product_id": pid,
            "amount": "100000",
            "term_months": 12,
            "purpose": "Тест",
            "monthly_income": "50000",
            "employment": "ИП",
        },
        headers=registered_user["headers"],
    )
    assert res.status_code == 422


def test_create_amount_out_of_range(client, registered_user, product_id):
    res = client.post(
        "/api/v1/applications",
        json={
            "credit_product_id": product_id,
            "amount": "99999999",
            "term_months": 12,
            "purpose": "Тест",
            "monthly_income": "50000",
            "employment": "ИП",
        },
        headers=registered_user["headers"],
    )
    assert res.status_code == 422


def test_create_term_out_of_range(client, registered_user, product_id):
    res = client.post(
        "/api/v1/applications",
        json={
            "credit_product_id": product_id,
            "amount": "100000",
            "term_months": 999,
            "purpose": "Тест",
            "monthly_income": "50000",
            "employment": "ИП",
        },
        headers=registered_user["headers"],
    )
    assert res.status_code == 422


# ---------- СПИСОК ----------

def test_list_returns_only_own_applications(
    client, registered_user, second_user, product_id
):
    for headers in (registered_user["headers"], second_user["headers"]):
        client.post(
            "/api/v1/applications",
            json={
                "credit_product_id": product_id,
                "amount": "100000",
                "term_months": 12,
                "purpose": "Тест",
                "monthly_income": "50000",
                "employment": "ИП",
            },
            headers=headers,
        )

    res_a = client.get("/api/v1/applications", headers=registered_user["headers"])
    res_b = client.get("/api/v1/applications", headers=second_user["headers"])

    assert res_a.status_code == 200
    assert res_b.status_code == 200
    assert len(res_a.json()) == 1
    assert len(res_b.json()) == 1
    assert res_a.json()[0]["user_id"] == registered_user["user"]["id"]
    assert res_b.json()[0]["user_id"] == second_user["user"]["id"]


# ---------- РЕДАКТИРОВАНИЕ ----------

def test_patch_draft_success(
    client, registered_user, user_a_id, create_draft_application
):
    app_id = create_draft_application(user_id=user_a_id, amount=100000)

    res = client.patch(
        f"/api/v1/applications/{app_id}",
        json={"amount": "200000"},
        headers=registered_user["headers"],
    )
    assert res.status_code == 200
    assert float(res.json()["amount"]) == 200000.0


def test_patch_submitted_returns_409(
    client, registered_user, user_a_id, create_draft_application
):
    app_id = create_draft_application(user_id=user_a_id, status="submitted")

    res = client.patch(
        f"/api/v1/applications/{app_id}",
        json={"amount": "200000"},
        headers=registered_user["headers"],
    )
    assert res.status_code == 409


# ---------- SUBMIT: APPROVED / REJECTED ----------

def test_submit_approved(client, registered_user, user_a_id, create_draft_application):
    # Доход 50000, платёж по 100000/12/15% ≈ 9025 → 18% дохода → approved
    app_id = create_draft_application(user_id=user_a_id, amount=100000, term_months=12)

    res = client.post(
        f"/api/v1/applications/{app_id}/submit",
        headers=registered_user["headers"],
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "approved"
    assert float(data["monthly_payment"]) > 0
    assert float(data["total_payment"]) > 0
    assert float(data["overpayment"]) > 0


def test_submit_rejected(client, registered_user, user_a_id, TestingSessionLocal, product_id):
    from app.models.credit_application import CreditApplication

    db = TestingSessionLocal()
    app_obj = CreditApplication(
        user_id=user_a_id,
        credit_product_id=product_id,
        amount=100000,
        term_months=12,
        purpose="Тест",
        monthly_income=5000,
        employment="ИП",
        status="draft",
    )
    db.add(app_obj)
    db.commit()
    db.refresh(app_obj)
    app_id = app_obj.id
    db.close()

    res = client.post(
        f"/api/v1/applications/{app_id}/submit",
        headers=registered_user["headers"],
    )
    assert res.status_code == 200
    assert res.json()["status"] == "rejected"


def test_submit_without_product(client, registered_user, user_a_id, TestingSessionLocal):
    from app.models.credit_application import CreditApplication

    db = TestingSessionLocal()
    app_obj = CreditApplication(
        user_id=user_a_id,
        credit_product_id=None,
        amount=100000,
        term_months=12,
        purpose="Тест",
        monthly_income=50000,
        employment="ИП",
        status="draft",
    )
    db.add(app_obj)
    db.commit()
    db.refresh(app_obj)
    app_id = app_obj.id
    db.close()

    res = client.post(
        f"/api/v1/applications/{app_id}/submit",
        headers=registered_user["headers"],
    )
    assert res.status_code == 422