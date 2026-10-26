"""Create deterministic synthetic demo data for Smart Credit Cabinet.

Run after Alembic migrations:
    python -m app.seed
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import (
    ApplicationHistory,
    BusinessProfile,
    CreditApplication,
    CreditProduct,
    User,
)

DEMO_PASSWORD = "DemoPass123!"

DEMO_USERS = [
    {
        "email": "staff@example.com",
        "role": "staff",
    },
    {
        "email": "owner.cafe@example.com",
        "role": "client",
    },
    {
        "email": "owner.shop@example.com",
        "role": "client",
    },
    {
        "email": "owner.factory@example.com",
        "role": "client",
    },
]

DEMO_PRODUCTS = [
    {
        "name": "Оборотный кредит для малого бизнеса",
        "bank_name": "Демо Банк",
        "interest_rate": Decimal("14.50"),
        "min_amount": Decimal("100000"),
        "max_amount": Decimal("5000000"),
        "min_term_months": 3,
        "max_term_months": 36,
        "commission_rate": Decimal("0.50"),
        "additional_conditions": "Синтетическое предложение для демонстрации",
        "description": "Финансирование закупок, аренды и текущих расходов.",
        "supported_purposes": ["working_capital", "business_expansion"],
        "min_business_age_months": 6,
        "requires_collateral": False,
        "is_active": True,
    },
    {
        "name": "Кредит на оборудование",
        "bank_name": "Демо Банк",
        "interest_rate": Decimal("12.90"),
        "min_amount": Decimal("300000"),
        "max_amount": Decimal("10000000"),
        "min_term_months": 6,
        "max_term_months": 60,
        "commission_rate": Decimal("0"),
        "additional_conditions": "Целевое финансирование покупки оборудования",
        "description": "Покупка производственного и торгового оборудования.",
        "supported_purposes": ["equipment", "business_expansion"],
        "min_business_age_months": 12,
        "requires_collateral": True,
        "is_active": True,
    },
    {
        "name": "Кредитная линия для предпринимателей",
        "bank_name": "Партнёрский Демо Банк",
        "interest_rate": Decimal("16.00"),
        "min_amount": Decimal("200000"),
        "max_amount": Decimal("3000000"),
        "min_term_months": 3,
        "max_term_months": 24,
        "commission_rate": Decimal("0"),
        "additional_conditions": "Лимит используется по мере необходимости",
        "description": "Гибкое финансирование текущих потребностей бизнеса.",
        "supported_purposes": ["working_capital"],
        "min_business_age_months": 3,
        "requires_collateral": False,
        "is_active": True,
    },
]

DEMO_BUSINESSES = [
    {
        "email": "owner.cafe@example.com",
        "business_name": "Кафе «Уют»",
        "legal_form": "IP",
        "industry": "Общественное питание",
        "region": "Москва",
        "business_start_date": date(2022, 5, 1),
        "monthly_revenue": Decimal("1200000"),
    },
    {
        "email": "owner.shop@example.com",
        "business_name": "Интернет-магазин «Покупай»",
        "legal_form": "OOO",
        "industry": "Электронная торговля",
        "region": "Санкт-Петербург",
        "business_start_date": date(2023, 2, 1),
        "monthly_revenue": Decimal("850000"),
    },
    {
        "email": "owner.factory@example.com",
        "business_name": "Мастерская «Профи»",
        "legal_form": "OOO",
        "industry": "Производство",
        "region": "Казань",
        "business_start_date": date(2021, 9, 1),
        "monthly_revenue": Decimal("2400000"),
    },
]


def get_or_create_user(db, email: str, role: str) -> User:
    email = email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))

    if user is None:
        user = User(
            email=email,
            hashed_password=hash_password(DEMO_PASSWORD),
            role=role,
        )
        db.add(user)
        db.flush()
    elif user.role != role:
        user.role = role

    return user


def seed_database() -> None:
    with SessionLocal() as db:
        try:
            # 1. Demo accounts
            users = {
                item["email"]: get_or_create_user(
                    db, item["email"], item["role"]
                )
                for item in DEMO_USERS
            }

            # 2. Credit products
            products = {}

            for item in DEMO_PRODUCTS:
                product = db.scalar(
                    select(CreditProduct).where(
                        CreditProduct.name == item["name"],
                        CreditProduct.bank_name == item["bank_name"],
                    )
                )

                if product is None:
                    product = CreditProduct(**item)
                    db.add(product)
                    db.flush()

                products[item["name"]] = product

            
            # 3. Business profiles
            for item in DEMO_BUSINESSES:
                user = users[item["email"]]

                profile = db.scalar(
                    select(BusinessProfile).where(
                        BusinessProfile.user_id == user.id
                    )
                )

                profile_data = {
                    key: value
                    for key, value in item.items()
                    if key != "email"
                }

                if profile is None:
                    profile = BusinessProfile(
                        user_id=user.id,
                        **profile_data,
                    )
                    db.add(profile)
                else:
                    # Заполняем и обновляем данные существующего профиля
                    for key, value in profile_data.items():
                        setattr(profile, key, value)

            db.flush()

            # 4. Demo applications with different statuses
            application_specs = [
                {
                    "email": "owner.cafe@example.com",
                    "product": "Оборотный кредит для малого бизнеса",
                    "amount": Decimal("800000"),
                    "term": 24,
                    "purpose": "working_capital",
                    "status": "submitted",
                    "comment": "Синтетическая заявка для демонстрации",
                },
                {
                    "email": "owner.shop@example.com",
                    "product": "Кредит на оборудование",
                    "amount": Decimal("1200000"),
                    "term": 36,
                    "purpose": "equipment",
                    "status": "draft",
                    "comment": "Покупка оборудования для склада",
                },
                {
                    "email": "owner.factory@example.com",
                    "product": "Кредитная линия для предпринимателей",
                    "amount": Decimal("1500000"),
                    "term": 18,
                    "purpose": "working_capital",
                    "status": "checking",
                    "comment": "Пополнение оборотных средств",
                },
            ]

            for spec in application_specs:
                user = users[spec["email"]]
                product = products[spec["product"]]

                existing = db.scalar(
                    select(CreditApplication).where(
                        CreditApplication.user_id == user.id,
                        CreditApplication.comment == spec["comment"],
                    )
                )

                if existing is not None:
                    continue

                application = CreditApplication(
                    user_id=user.id,
                    credit_product_id=product.id,
                    amount=spec["amount"],
                    term_months=spec["term"],
                    purpose=spec["purpose"],
                    monthly_income=Decimal("150000"),
                    organization_name=next(
                        business["business_name"]
                        for business in DEMO_BUSINESSES
                        if business["email"] == spec["email"]
                    ),
                    organization_type=next(
                        business["legal_form"]
                        for business in DEMO_BUSINESSES
                        if business["email"] == spec["email"]
                    ),
                    status=spec["status"],
                    comment=spec["comment"],
                )
                db.add(application)
                db.flush()

                db.add(
                    ApplicationHistory(
                        application_id=application.id,
                        old_status=None,
                        new_status=application.status,
                        comment="Заявка создана автоматически для демо",
                    )
                )

            db.commit()

            print("Synthetic demo data created or already exists.")
            print("Demo accounts (same password for all):")
            for item in DEMO_USERS:
                print(f"  {item['email']} — {DEMO_PASSWORD}")
            print(f"Credit products: {len(DEMO_PRODUCTS)}")
            print(f"Business profiles: {len(DEMO_BUSINESSES)}")

        except Exception:
            db.rollback()
            raise


if __name__ == "__main__":
    seed_database()
