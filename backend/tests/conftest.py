import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.models.credit_application import CreditApplication
from app.models.credit_product import CreditProduct

SQLALCHEMY_DATABASE_URL = "sqlite://"


@pytest.fixture(scope="function")
def db_engine():
    """Один in-memory движок на тест. StaticPool = одно соединение = одна база."""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def TestingSessionLocal(db_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


@pytest.fixture(scope="function")
def client(db_engine, TestingSessionLocal):
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def registered_user(client):
    """Регистрирует test_a@test.com и возвращает (user_data, headers)."""
    email = "test_a@test.com"
    password = "password123"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    res = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    token = res.json()["access_token"]
    user = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    ).json()
    return {
        "user": user,
        "headers": {"Authorization": f"Bearer {token}"},
        "email": email,
        "password": password,
    }


@pytest.fixture(scope="function")
def second_user(client):
    """Регистрирует test_b@test.com и возвращает (user_data, headers)."""
    email = "test_b@test.com"
    password = "password123"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    res = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    token = res.json()["access_token"]
    user = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    ).json()
    return {
        "user": user,
        "headers": {"Authorization": f"Bearer {token}"},
        "email": email,
        "password": password,
    }


@pytest.fixture(scope="function")
def auth_headers(registered_user, second_user):
    """Совместимость со старыми тестами: {'a': headers, 'b': headers}."""
    return {
        "a": registered_user["headers"],
        "b": second_user["headers"],
    }


@pytest.fixture(scope="function")
def user_a_id(client, registered_user):
    return registered_user["user"]["id"]


@pytest.fixture(scope="function")
def product_id(client, TestingSessionLocal):
    db = TestingSessionLocal()
    product = CreditProduct(
        name="Тестовый продукт",
        bank_name="Тестовый банк",
        min_amount=10000,
        max_amount=1000000,
        min_term_months=6,
        max_term_months=36,
        interest_rate=15.0,
        is_active=True,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    pid = product.id
    db.close()
    return pid


@pytest.fixture(scope="function")
def create_draft_application(client, TestingSessionLocal, product_id):
    """Фабрика: создаёт заявку в БД и возвращает её id."""

    def _create(user_id, status="draft", amount=100000, term_months=12):
        db = TestingSessionLocal()
        app_obj = CreditApplication(
            user_id=user_id,
            credit_product_id=product_id,
            amount=amount,
            term_months=term_months,
            purpose="Тест",
            monthly_income=50000,
            employment="ИП",
            status=status,
        )
        db.add(app_obj)
        db.commit()
        db.refresh(app_obj)
        app_id = app_obj.id
        db.close()
        return app_id

    return _create