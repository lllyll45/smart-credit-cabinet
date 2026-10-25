from app.models.credit_application import CreditApplication


def _create_draft(TestingSessionLocal, user_a_id, product_id):
    db = TestingSessionLocal()
    app_obj = CreditApplication(
        user_id=user_a_id,
        credit_product_id=product_id,
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
    return app_id


def test_cannot_read_other_application(
    client, auth_headers, product_id, user_a_id, TestingSessionLocal
):
    app_id = _create_draft(TestingSessionLocal, user_a_id, product_id)

    res_b = client.get(f"/api/v1/applications/{app_id}", headers=auth_headers["b"])
    assert res_b.status_code == 404


def test_cannot_edit_submitted_application(
    client, auth_headers, product_id, user_a_id, TestingSessionLocal
):
    app_id = _create_draft(TestingSessionLocal, user_a_id, product_id)

    client.post(f"/api/v1/applications/{app_id}/submit", headers=auth_headers["a"])

    res_patch = client.patch(
        f"/api/v1/applications/{app_id}",
        json={"amount": 200000},
        headers=auth_headers["a"],
    )
    assert res_patch.status_code == 409


def test_cannot_resubmit(
    client, auth_headers, product_id, user_a_id, TestingSessionLocal
):
    app_id = _create_draft(TestingSessionLocal, user_a_id, product_id)

    client.post(f"/api/v1/applications/{app_id}/submit", headers=auth_headers["a"])

    res_submit = client.post(
        f"/api/v1/applications/{app_id}/submit", headers=auth_headers["a"]
    )
    assert res_submit.status_code == 409


def test_not_found_id(client, auth_headers):
    res = client.get("/api/v1/applications/9999", headers=auth_headers["a"])
    assert res.status_code == 404


def test_invalid_data(client, auth_headers):
    res = client.post(
        "/api/v1/applications",
        json={
            "amount": -100,
            "term_months": 12,
            "purpose": "Тест",
            "monthly_income": 50000,
            "employment": "ИП",
            "credit_product_id": 1,
        },
        headers=auth_headers["a"],
    )
    assert res.status_code == 422