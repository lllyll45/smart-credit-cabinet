"""Тесты истории изменения статусов заявки."""


def _create_application(client, headers, product_id):
    res = client.post(
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
    assert res.status_code == 201
    return res.json()["id"]


def test_history_recorded_on_create(client, registered_user, product_id):
    """При создании заявки в историю пишется old_status=None, new_status=draft."""
    app_id = _create_application(
        client, registered_user["headers"], product_id
    )

    history_res = client.get(
        f"/api/v1/applications/{app_id}/history",
        headers=registered_user["headers"],
    )
    assert history_res.status_code == 200
    history = history_res.json()
    assert len(history) == 1
    assert history[0]["old_status"] is None
    assert history[0]["new_status"] == "draft"
    assert "создана" in history[0]["comment"].lower()


def test_history_recorded_on_submit(client, registered_user, product_id):
    """После submit в истории 2 записи: draft → submitted."""
    app_id = _create_application(
        client, registered_user["headers"], product_id
    )

    client.post(
        f"/api/v1/applications/{app_id}/submit",
        headers=registered_user["headers"],
    )

    history_res = client.get(
        f"/api/v1/applications/{app_id}/history",
        headers=registered_user["headers"],
    )
    assert history_res.status_code == 200
    history = history_res.json()
    assert len(history) == 2
    assert history[0]["old_status"] is None
    assert history[0]["new_status"] == "draft"
    assert history[1]["old_status"] == "draft"
    assert history[1]["new_status"] == "submitted"


def test_history_404_for_missing_application(client, registered_user):
    res = client.get(
        "/api/v1/applications/999999/history",
        headers=registered_user["headers"],
    )
    assert res.status_code == 404


def test_history_404_for_other_user_application(
    client, registered_user, second_user, product_id
):
    """Пользователь B не видит историю заявки пользователя A."""
    app_id = _create_application(
        client, registered_user["headers"], product_id
    )

    history_res = client.get(
        f"/api/v1/applications/{app_id}/history",
        headers=second_user["headers"],
    )
    assert history_res.status_code == 404


def test_history_requires_auth(client):
    res = client.get("/api/v1/applications/1/history")
    assert res.status_code == 401
