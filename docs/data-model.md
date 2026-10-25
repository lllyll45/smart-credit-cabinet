# Модель данных — Smart Credit Cabinet

Модель данных соответствует текущей реализации. В базе **7 таблиц**:
`users`, `credit_products`, `credit_applications`, `application_history`, `business_profiles`, `recommendations`, `recommendation_items`.

СУБД: PostgreSQL. ORM: SQLAlchemy. Миграции: Alembic.

## 1. users — пользователи

| Поле | Тип | Описание |
|---|---|---|
| `id` | INTEGER, PK | Идентификатор |
| `email` | VARCHAR(255), UNIQUE, NOT NULL | Почта |
| `hashed_password` | VARCHAR(255), NOT NULL | Хеш пароля (Argon2) |
| `role` | VARCHAR(20), NOT NULL | `client` / `staff` / `admin` |
| `created_at` | TIMESTAMPTZ, NOT NULL | Дата регистрации |

Связи:
- `applications` — один ко многим с `credit_applications`
- `business_profile` — один к одному с `business_profiles` (`uselist=False`)

## 2. credit_products — кредитные продукты

| Поле | Тип | Описание |
|---|---|---|
| `id` | INTEGER, PK | Идентификатор |
| `name` | VARCHAR(200), NOT NULL | Название |
| `bank_name` | VARCHAR(150), NOT NULL | Банк |
| `interest_rate` | NUMERIC(5,2), NOT NULL | Годовая ставка, % |
| `min_amount`, `max_amount` | NUMERIC(15,2), NOT NULL | Диапазон суммы |
| `min_term_months`, `max_term_months` | INTEGER, NOT NULL | Диапазон срока |
| `commission_rate` | NUMERIC(5,2), NULL | Комиссия, % от суммы |
| `commission_amount` | NUMERIC(15,2), NULL | Фиксированная комиссия |
| `additional_conditions` | TEXT, NULL | Условия |
| `description` | TEXT, NULL | Описание |
| `supported_purposes` | JSONB, NOT NULL | Поддерживаемые цели (`["working_capital", ...]`) |
| `min_business_age_months` | INTEGER, NULL | Минимальный возраст бизнеса |
| `requires_collateral` | BOOLEAN, NOT NULL | Нужно ли обеспечение |
| `is_active` | BOOLEAN, NOT NULL | Доступность |
| `created_at`, `updated_at` | TIMESTAMPTZ, NOT NULL | Метки времени |

Примечание: в тестах (SQLite) `JSONB` заменяется на `JSON` через `app/core/json_type.JSONType`.

Связи:
- `applications` — один ко многим с `credit_applications`
- `recommendation_items` — один ко многим с `recommendation_items`

## 3. credit_applications — кредитные заявки

| Поле | Тип | Описание |
|---|---|---|
| `id` | INTEGER, PK | Идентификатор |
| `user_id` | INTEGER, FK → users.id, NOT NULL | Владелец |
| `credit_product_id` | INTEGER, FK → credit_products.id, NULL | Выбранный продукт |
| `amount` | NUMERIC(12,2), NOT NULL | Сумма |
| `term_months` | INTEGER, NOT NULL | Срок |
| `purpose` | VARCHAR(255), NOT NULL | Цель |
| `monthly_income` | NUMERIC(12,2), NULL | Доход |
| `employment` | VARCHAR(255), NULL | Занятость |
| `status` | VARCHAR(50), NOT NULL | Статус заявки |
| `comment` | TEXT, NULL | Комментарий |
| `decision_comment` | TEXT, NULL | Комментарий к решению |
| `preliminary_result` | VARCHAR(50), NULL | `likely_eligible` / `high_debt_burden` |
| `monthly_payment` | NUMERIC(12,2), NULL | Платёж |
| `total_payment` | NUMERIC(12,2), NULL | Общая сумма |
| `overpayment` | NUMERIC(12,2), NULL | Переплата |
| `created_at`, `updated_at` | TIMESTAMPTZ, NOT NULL | Метки времени |

Связи:
- `user` — многие к одному
- `credit_product` — многие к одному
- `history` — один ко многим с `application_history` (каскадное удаление)

## 4. application_history — история статусов

| Поле | Тип | Описание |
|---|---|---|
| `id` | INTEGER, PK | Идентификатор |
| `application_id` | INTEGER, FK → credit_applications.id, NOT NULL | Заявка |
| `old_status` | VARCHAR(50), NULL | Предыдущий статус (`null` при создании) |
| `new_status` | VARCHAR(50), NOT NULL | Новый статус |
| `comment` | TEXT, NULL | Комментарий |
| `created_at` | TIMESTAMPTZ, NOT NULL | Дата события |

Пишется при: создании (`None` → `draft`), submit (`draft` → `submitted`), approve/reject/check/request-info/offer-alternative.

## 5. business_profiles — профили бизнеса

| Поле | Тип | Описание |
|---|---|---|
| `id` | INTEGER, PK | Идентификатор |
| `user_id` | INTEGER, FK → users.id, UNIQUE, NOT NULL | Владелец |
| `business_name` | VARCHAR(255), NOT NULL | Название бизнеса |
| `legal_form` | VARCHAR(20), NOT NULL | `IP` или `OOO` |
| `industry` | VARCHAR(100), NULL | Отрасль |
| `region` | VARCHAR(100), NULL | Регион |
| `business_start_date` | DATE, NULL | Дата начала |
| `monthly_revenue` | NUMERIC(15,2), NULL | Среднемесячная выручка |
| `created_at`, `updated_at` | TIMESTAMPTZ, NOT NULL | Метки времени |

`UNIQUE user_id` = один профиль на пользователя.

## 6. recommendations — подборы предложений

| Поле | Тип | Описание |
|---|---|---|
| `id` | INTEGER, PK | Идентификатор |
| `user_id` | INTEGER, FK → users.id, NOT NULL | Пользователь |
| `requested_amount` | NUMERIC(15,2), NOT NULL | Запрошенная сумма |
| `term_months` | INTEGER, NOT NULL | Срок |
| `purpose` | VARCHAR(100), NOT NULL | Цель |
| `monthly_revenue` | NUMERIC(15,2), NULL | Выручка (для скоринга) |
| `business_age_months` | INTEGER, NULL | Возраст бизнеса |
| `created_at` | TIMESTAMPTZ, NOT NULL | Дата подбора |

Связи:
- `items` — один ко многим с `recommendation_items` (сортировка по `match_score desc`)

## 7. recommendation_items — продукты в подборе

| Поле | Тип | Описание |
|---|---|---|
| `id` | INTEGER, PK | Идентификатор |
| `recommendation_id` | INTEGER, FK → recommendations.id, NOT NULL | Подбор |
| `product_id` | INTEGER, FK → credit_products.id, NOT NULL | Продукт |
| `match_score` | NUMERIC(5,2), NOT NULL | Оценка 0..100 |
| `estimated_monthly_payment` | NUMERIC(15,2), NULL | Ожидаемый платёж |
| `reasons` | JSONB, NOT NULL | Массив причин (`["Сумма входит в диапазон", ...]`) |
| `created_at` | TIMESTAMPTZ, NOT NULL | Дата |

Связи:
- `recommendation` — многие к одному
- `product` — многие к одному

## 8. Статусы заявки

| Статус | Значение |
|---|---|
| `draft` | Черновик, доступен для редактирования |
| `submitted` | Отправлена, только чтение |
| `checking` | На проверке (staff) |
| `needs_info` | Требуется дополнительная информация (staff) |
| `alternative_offer` | Предложены альтернативные условия (staff) |
| `approved` | Одобрена (staff) |
| `rejected` | Отклонена (staff) |

`preliminary_result`:
- `likely_eligible` — платёж ≤ 40% дохода
- `high_debt_burden` — платёж > 40% дохода

Это **предварительная** оценка, не финальное решение.

## 9. Формула `match_score`

Взвешенная оценка 0..100:
- сумма в диапазоне — 40%
- срок в диапазоне — 30%
- доход (платёж / доход) — 20%: `≤40%` → 1.0, `40–60%` → 0.5, `>60%` → 0
- возраст бизнеса ≥ минимума — 10%

Если продукт не подходит по сумме, сроку, цели или возрасту — он **отсеивается** (не попадает в `recommendation_items`).

## 10. Ограничения

- Email уникален
- Сумма и срок положительны
- Продукт существует и активен
- Пользователь видит только свои заявки / профиль / подборы
- Пароли хранятся в виде хеша
- Деньги — в `NUMERIC`, не `float`

## 11. Миграции Alembic

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
| `c3d4e5f6a7b8` | `recommendations`, `recommendation_items` + новые поля `credit_products` |

Применение: `alembic upgrade head`. Создание новой: `alembic revision --autogenerate -m "..."`.

## 12. Не реализовано (в отличие от старой версии документа)

Сущности `Verification`, `CreditDecision` — в планах, в коде отсутствуют. Решения по заявке (`approved`/`rejected`) хранятся в `credit_applications.status` и `credit_applications.decision_comment`, отдельной таблицы нет.