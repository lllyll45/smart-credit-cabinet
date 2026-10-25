# Модель данных — Smart Credit Cabinet

СУБД: PostgreSQL. ORM: SQLAlchemy. Миграции: Alembic. В реализации — **7 таблиц**.

## 1. ER-диаграмма

```mermaid
erDiagram
    USERS ||--o{ CREDIT_APPLICATIONS : creates
    USERS ||--o| BUSINESS_PROFILES : owns
    USERS ||--o{ RECOMMENDATIONS : requests
    CREDIT_PRODUCTS ||--o{ CREDIT_APPLICATIONS : selected_for
    CREDIT_PRODUCTS ||--o{ RECOMMENDATION_ITEMS : included_in
    RECOMMENDATIONS ||--o{ RECOMMENDATION_ITEMS : contains
    CREDIT_APPLICATIONS ||--o{ APPLICATION_HISTORY : records

    USERS {
        int id PK
        string email UK
        string hashed_password
        string role
        datetime created_at
    }
    CREDIT_PRODUCTS {
        int id PK
        string name
        string bank_name
        decimal interest_rate
        decimal min_amount
        decimal max_amount
        int min_term_months
        int max_term_months
        decimal commission_rate
        decimal commission_amount
        text description
        text additional_conditions
        jsonb supported_purposes
        int min_business_age_months
        boolean requires_collateral
        boolean is_active
    }
    CREDIT_APPLICATIONS {
        int id PK
        int user_id FK
        int credit_product_id FK
        decimal amount
        int term_months
        string purpose
        decimal monthly_income
        string employment
        string status
        string preliminary_result
        decimal monthly_payment
        decimal total_payment
        decimal overpayment
    }
    APPLICATION_HISTORY {
        int id PK
        int application_id FK
        string old_status
        string new_status
        text comment
        datetime created_at
    }
    BUSINESS_PROFILES {
        int id PK
        int user_id FK,UK
        string business_name
        string legal_form
        string industry
        string region
        date business_start_date
        decimal monthly_revenue
    }
    RECOMMENDATIONS {
        int id PK
        int user_id FK
        decimal requested_amount
        int term_months
        string purpose
        decimal monthly_revenue
        int business_age_months
    }
    RECOMMENDATION_ITEMS {
        int id PK
        int recommendation_id FK
        int product_id FK
        decimal match_score
        decimal estimated_monthly_payment
        jsonb reasons
    }
```

## 2. Таблицы

### `users`
- `id` — PK;
- `email` — VARCHAR(255), UNIQUE, NOT NULL;
- `hashed_password` — VARCHAR(255), NOT NULL (Argon2);
- `role` — VARCHAR(20), NOT NULL, default `client`; значения `client`, `staff`, `admin`;
- `created_at` — TIMESTAMPTZ, NOT NULL.

Связи: `applications` (1:N), `business_profile` (1:1, `uselist=False`).

### `credit_products`
- `id` — PK;
- `name` — VARCHAR(200), NOT NULL;
- `bank_name` — VARCHAR(150), NOT NULL;
- `interest_rate` — NUMERIC(5,2), NOT NULL;
- `min_amount`, `max_amount` — NUMERIC(15,2), NOT NULL;
- `min_term_months`, `max_term_months` — INTEGER, NOT NULL;
- `commission_rate` — NUMERIC(5,2), NULL;
- `commission_amount` — NUMERIC(15,2), NULL;
- `description` — TEXT, NULL;
- `additional_conditions` — TEXT, NULL;
- `supported_purposes` — JSONB, NOT NULL, default `[]`;
- `min_business_age_months` — INTEGER, NULL;
- `requires_collateral` — BOOLEAN, NOT NULL, default `false`;
- `is_active` — BOOLEAN, NOT NULL, default `true`;
- `created_at`, `updated_at` — TIMESTAMPTZ, NOT NULL.

Примечание: в тестах на SQLite `JSONB` заменяется на `JSON` через `app/core/json_type.JSONType`.

### `credit_applications`
- `id` — PK;
- `user_id` — FK → `users.id`, NOT NULL, `ondelete=CASCADE`;
- `credit_product_id` — FK → `credit_products.id`, NULL, `ondelete=SET NULL`;
- `amount` — NUMERIC(12,2), NOT NULL;
- `term_months` — INTEGER, NOT NULL;
- `purpose` — VARCHAR(255), NOT NULL;
- `monthly_income` — NUMERIC(12,2), NULL;
- `employment` — VARCHAR(255), NULL;
- `status` — VARCHAR(50), NOT NULL, default `draft`;
- `comment` — TEXT, NULL;
- `decision_comment` — TEXT, NULL;
- `preliminary_result` — VARCHAR(50), NULL (`likely_eligible` / `high_debt_burden`);
- `monthly_payment`, `total_payment`, `overpayment` — NUMERIC(12,2), NULL;
- `created_at`, `updated_at` — TIMESTAMPTZ, NOT NULL.

Связи: `user` (N:1), `credit_product` (N:1), `history` (1:N, `cascade="all, delete-orphan"`, `order_by=created_at`).

### `application_history`
- `id` — PK;
- `application_id` — FK → `credit_applications.id`, NOT NULL, `ondelete=CASCADE`;
- `old_status` — VARCHAR(50), NULL (NULL при создании);
- `new_status` — VARCHAR(50), NOT NULL;
- `comment` — TEXT, NULL;
- `created_at` — TIMESTAMPTZ, NOT NULL.

### `business_profiles`
- `id` — PK;
- `user_id` — FK → `users.id`, NOT NULL, UNIQUE, `ondelete=CASCADE`;
- `business_name` — VARCHAR(255), NOT NULL;
- `legal_form` — VARCHAR(20), NOT NULL (`IP` / `OOO`);
- `industry` — VARCHAR(100), NULL;
- `region` — VARCHAR(100), NULL;
- `business_start_date` — DATE, NULL;
- `monthly_revenue` — NUMERIC(15,2), NULL;
- `created_at`, `updated_at` — TIMESTAMPTZ, NOT NULL.

`UNIQUE user_id` = один профиль на пользователя.

### `recommendations`
- `id` — PK;
- `user_id` — FK → `users.id`, NOT NULL, `ondelete=CASCADE`;
- `requested_amount` — NUMERIC(15,2), NOT NULL;
- `term_months` — INTEGER, NOT NULL;
- `purpose` — VARCHAR(100), NOT NULL;
- `monthly_revenue` — NUMERIC(15,2), NULL;
- `business_age_months` — INTEGER, NULL;
- `created_at` — TIMESTAMPTZ, NOT NULL.

Связи: `items` (1:N, `cascade="all, delete-orphan"`, сортировка по `match_score desc`).

### `recommendation_items`
- `id` — PK;
- `recommendation_id` — FK → `recommendations.id`, NOT NULL, `ondelete=CASCADE`;
- `product_id` — FK → `credit_products.id`, NOT NULL, `ondelete=CASCADE`;
- `match_score` — NUMERIC(5,2), NOT NULL;
- `estimated_monthly_payment` — NUMERIC(15,2), NULL;
- `reasons` — JSONB, NOT NULL, default `[]`;
- `created_at` — TIMESTAMPTZ, NOT NULL.

## 3. Бизнес-правила

- `email` уникален.
- Деньги — `NUMERIC`, не `float`.
- Продукт заявки должен существовать и быть активным.
- Пользователь видит только свои заявки, профиль и подборы.
- `approved` и `rejected` — финальные статусы.
- `preliminary_result` — предварительная оценка, не банковское решение.
- `match_score` — взвешенная оценка: сумма 40%, срок 30%, доход 20%, возраст бизнеса 10%; неподходящие продукты отсеиваются.

## 4. Миграции Alembic

| Ревизия | Что делает |
|---|---|
| `711a25141bf5` | Создание `users` |
| `d2eefc340c25` | Создание `credit_applications` |
| `61ffaf4ab915` | Создание `credit_products` |
| `a654ae10dd13` | Связь заявок с продуктами |
| `958ca098cb81` | `credit_product_id` в заявках |
| `4661d4878f2d` | Поля решения и платежей |
| `4544c5ffb92f` | Роль пользователя |
| `3fb1579ae565` | Предварительный результат |
| `53d00dceb9da` | Дополнение предварительного результата |
| `a1b2c3d4e5f6` | `application_history` |
| `b2c3d4e5f6a7` | `business_profiles` |
| `c3d4e5f6a7b8` | `recommendations`, `recommendation_items`, новые поля `credit_products` |

Применение: `alembic upgrade head` из `backend/`.
