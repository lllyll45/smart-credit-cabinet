
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.credit_product import CreditProduct


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        bind=engine,
        class_=Session,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        with TestingSessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestingSessionLocal() as db:
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

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_get_products_returns_active_products(client):
    response = client.get("/api/v1/products")

    assert response.status_code == 200

    products = response.json()
    assert len(products) == 1
    assert products[0]["name"] == "Потребительский кредит"
    assert products[0]["bank_name"] == "Альфа-Банк"
    assert products[0]["interest_rate"] == "19.90"


def test_get_product_by_id(client):
    products_response = client.get("/api/v1/products")
    product_id = products_response.json()[0]["id"]

    response = client.get(f"/api/v1/products/{product_id}")

    assert response.status_code == 200
    assert response.json()["id"] == product_id
    assert response.json()["bank_name"] == "Альфа-Банк"


def test_get_missing_product_returns_404(client):
    response = client.get("/api/v1/products/999999")

    assert response.status_code == 404


def test_get_inactive_product_returns_404(client):
    products_response = client.get("/api/v1/products")
    active_product_id = products_response.json()[0]["id"]

    # У неактивного продукта отдельный ID; получаем его из тестовой БД.
    from sqlalchemy import select

    with next(app.dependency_overrides[get_db]()) as db:
        inactive_product = db.scalar(
            select(CreditProduct).where(CreditProduct.is_active.is_(False))
        )
        inactive_product_id = inactive_product.id

    assert inactive_product_id != active_product_id

    response = client.get(f"/api/v1/products/{inactive_product_id}")

    assert response.status_code == 404
