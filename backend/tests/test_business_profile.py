"""Тесты профиля бизнеса."""


def test_get_business_profile_404_when_missing(client, registered_user):
    """Если профиль не создан — GET возвращает 404."""
    res = client.get(
        "/api/v1/business-profile",
        headers=registered_user["headers"],
    )
    assert res.status_code == 404


def test_create_business_profile(client, registered_user):
    """PUT создаёт профиль и возвращает данные."""
    res = client.put(
        "/api/v1/business-profile",
        json={
            "business_name": "ООО Ромашка",
            "legal_form": "OOO",
            "industry": "Торговля",
            "region": "Республика Башкортостан",
            "business_start_date": "2022-05-01",
            "monthly_revenue": "850000.00",
        },
        headers=registered_user["headers"],
    )
    assert res.status_code == 200
    data = res.json()
    assert data["business_name"] == "ООО Ромашка"
    assert data["legal_form"] == "OOO"
    assert data["industry"] == "Торговля"
    assert data["region"] == "Республика Башкортостан"
    assert float(data["monthly_revenue"]) == 850000.0


def test_update_business_profile(client, registered_user):
    """PUT обновляет существующий профиль (upsert)."""
    client.put(
        "/api/v1/business-profile",
        json={
            "business_name": "ООО Ромашка",
            "legal_form": "OOO",
            "monthly_revenue": "850000.00",
        },
        headers=registered_user["headers"],
    )

    res = client.put(
        "/api/v1/business-profile",
        json={
            "business_name": "ООО Лютик",
            "legal_form": "IP",
            "monthly_revenue": "950000.00",
        },
        headers=registered_user["headers"],
    )
    assert res.status_code == 200
    data = res.json()
    assert data["business_name"] == "ООО Лютик"
    assert data["legal_form"] == "IP"
    assert float(data["monthly_revenue"]) == 950000.0


def test_get_business_profile_after_create(client, registered_user):
    """После PUT — GET возвращает тот же профиль."""
    client.put(
        "/api/v1/business-profile",
        json={
            "business_name": "ООО Ромашка",
            "legal_form": "OOO",
            "industry": "Торговля",
        },
        headers=registered_user["headers"],
    )

    res = client.get(
        "/api/v1/business-profile",
        headers=registered_user["headers"],
    )
    assert res.status_code == 200
    assert res.json()["business_name"] == "ООО Ромашка"
    assert res.json()["industry"] == "Торговля"


def test_invalid_legal_form_returns_422(client, registered_user):
    """legal_form должен быть IP или OOO."""
    res = client.put(
        "/api/v1/business-profile",
        json={
            "business_name": "ООО Ромашка",
            "legal_form": "INVALID",
        },
        headers=registered_user["headers"],
    )
    assert res.status_code == 422


def test_business_profile_requires_auth(client):
    """Без токена — 401."""
    res = client.get("/api/v1/business-profile")
    assert res.status_code == 401


def test_profiles_isolated_between_users(
    client, registered_user, second_user
):
    """Профили разных пользователей независимы."""
    client.put(
        "/api/v1/business-profile",
        json={
            "business_name": "A Business",
            "legal_form": "IP",
        },
        headers=registered_user["headers"],
    )
    client.put(
        "/api/v1/business-profile",
        json={
            "business_name": "B Business",
            "legal_form": "OOO",
        },
        headers=second_user["headers"],
    )

    res_a = client.get(
        "/api/v1/business-profile",
        headers=registered_user["headers"],
    )
    res_b = client.get(
        "/api/v1/business-profile",
        headers=second_user["headers"],
    )

    assert res_a.json()["business_name"] == "A Business"
    assert res_b.json()["business_name"] == "B Business"
