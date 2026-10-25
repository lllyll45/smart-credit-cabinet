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
def auth_headers(client):
    client.post("/api/v1/auth/register", json={"email": "test_a@test.com", "password": "password123"})
    client.post("/api/v1/auth/register", json={"email": "test_b@test.com", "password": "password123"})

    res_a = client.post("/api/v1/auth/login", data={"username": "test_a@test.com", "password": "password123"})
    token_a = res_a.json()["access_token"]

    res_b = client.post("/api/v1/auth/login", data={"username": "test_b@test.com", "password": "password123"})
    token_b = res_b.json()["access_token"]

    return {
        "a": {"Authorization": f"Bearer {token_a}"},
        "b": {"Authorization": f"Bearer {token_b}"},
    }


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
def user_a_id(client, auth_headers, TestingSessionLocal):
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "test_a@test.com").first()
    assert user is not None, "Пользователь test_a@test.com не найден — auth_headers не отработал?"
    uid = user.id
    db.close()
    return uid