
from decimal import Decimal

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.credit_product import CreditProduct



DEMO_PRODUCTS = [
    {
        "name": "Потребительский кредит",
        "bank_name": "Альфа-Банк",
        "interest_rate": Decimal("19.90"),
        "min_amount": Decimal("50000.00"),
        "max_amount": Decimal("5000000.00"),
        "min_term_months": 6,
        "max_term_months": 60,
        "commission_rate": Decimal("0.00"),
        "commission_amount": Decimal("0.00"),
        "additional_conditions": (
            "Демонстрационные условия для прототипа. "
            "Не являются официальным предложением банка."
        ),
    },
    {
        "name": "Кредит на крупную покупку",
        "bank_name": "Альфа-Банк",
        "interest_rate": Decimal("21.50"),
        "min_amount": Decimal("100000.00"),
        "max_amount": Decimal("3000000.00"),
        "min_term_months": 12,
        "max_term_months": 84,
        "commission_rate": Decimal("0.00"),
        "commission_amount": Decimal("0.00"),
        "additional_conditions": (
            "Демонстрационные условия для прототипа. "
            "Не являются официальным предложением банка."
        ),
    },
    {
        "name": "Кредит на любые цели",
        "bank_name": "Альфа-Банк",
        "interest_rate": Decimal("24.90"),
        "min_amount": Decimal("30000.00"),
        "max_amount": Decimal("2000000.00"),
        "min_term_months": 3,
        "max_term_months": 60,
        "commission_rate": Decimal("1.00"),
        "commission_amount": None,
        "additional_conditions": (
            "Демонстрационные условия для прототипа. "
            "Комиссия 1% задана для тестирования расчётов."
        ),
    },
]



def seed_products() -> None:
    with SessionLocal() as db:
        added = 0

        for product_data in DEMO_PRODUCTS:
            existing = db.scalar(
                select(CreditProduct).where(
                    CreditProduct.name == product_data["name"],
                    CreditProduct.bank_name == product_data["bank_name"],
                )
            )

            if existing is None:
                db.add(CreditProduct(**product_data))
                added += 1

        db.commit()
        print(f"Добавлено продуктов: {added}")


if __name__ == "__main__":
    seed_products()
