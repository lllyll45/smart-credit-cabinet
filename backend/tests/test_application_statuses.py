"""Тесты новых статусов заявки: checking, needs_info, alternative_offer."""

import pytest

from app.models.user import User


@pytest.fixture(scope="function")
def staff_headers(client, TestingSessionLocal):
    """Регистрирует staff-пользователя и возвращает его заголовки."""
    email = "staff@test.com"
    password = "password123"

    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )

    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == email).first()
    user.role = "staff"
    db.commit()
    db.close()

    res = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _make_submitted_application(
    client, registered_user, product_id
):
    created = client.post(
        "/api/v1/applications",
        json={
            "credit_product_id": product_id,
            "amount": "100000",
            "term_months": 12,
            "purpose": "Тест",
            "monthly_income": "50000",
            "employment": "ИП",
        },
        headers=registered_user["headers"],
    )
    app_id = created.json()["id"]

    client.post(
        f"/api/v1/applications/{app_id}/submit",
        headers=registered_user["headers"],
    )
    return app_id


def test_staff_can_move_to_checking(
    client, registered_user, staff_headers, product_id
):
    app_id = _make_submitted_application(
        client, registered_user, product_id
    )

    res = client.post(
        f"/api/v1/applications/{app_id}/check",
        headers=staff_headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "checking"


def test_client_cannot_move_to_checking(
    client, registered_user, product_id
):
    app_id = _make_submitted_application(
        client, registered_user, product_id
    )

    res = client.post(
        f"/api/v1/applications/{app_id}/check",
        headers=registered_user["headers"],
    )
    assert res.status_code == 403


def test_staff_can_request_info(
    client, registered_user, staff_headers, product_id
):
    app_id = _make_submitted_application(
        client, registered_user, product_id
    )

    res = client.post(
        f"/api/v1/applications/{app_id}/request-info",
        headers=staff_headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "needs_info"


def test_staff_can_offer_alternative(
    client, registered_user, staff_headers, product_id
):
    app_id = _make_submitted_application(
        client, registered_user, product_id
    )

    res = client.post(
        f"/api/v1/applications/{app_id}/offer-alternative",
        headers=staff_headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "alternative_offer"


def test_checking_recorded_in_history(
    client, registered_user, staff_headers, product_id
):
    app_id = _make_submitted_application(
        client, registered_user, product_id
    )

    client.post(
        f"/api/v1/applications/{app_id}/check",
        headers=staff_headers,
    )

    history = client.get(
        f"/api/v1/applications/{app_id}/history",
        headers=registered_user["headers"],
    ).json()

    statuses = [h["new_status"] for h in history]
    assert "draft" in statuses
    assert "submitted" in statuses
    assert "checking" in statuses


def test_cannot_check_draft_application(
    client, registered_user, staff_headers, product_id
):
    created = client.post(
        "/api/v1/applications",
        json={
            "credit_product_id": product_id,
            "amount": "100000",
            "term_months": 12,
            "purpose": "Тест",
            "monthly_income": "50000",
            "employment": "ИП",
        },
        headers=registered_user["headers"],
    )
    app_id = created.json()["id"]

    res = client.post(
        f"/api/v1/applications/{app_id}/check",
        headers=staff_headers,
    )
    assert res.status_code == 409


def test_cannot_check_twice(
    client, registered_user, staff_headers, product_id
):
    app_id = _make_submitted_application(
        client, registered_user, product_id
    )

    client.post(
        f"/api/v1/applications/{app_id}/check",
        headers=staff_headers,
    )

    res = client.post(
        f"/api/v1/applications/{app_id}/check",
        headers=staff_headers,
    )
    assert res.status_code == 409
