# API Smart Credit Cabinet

Базовый префикс: `/api/v1`. Защищённые эндпоинты требуют заголовок `Authorization: Bearer <token>`.

## 1. Аккаунт и авторизация

| Метод | Путь | Авторизация | Назначение |
|---|---|---|---|
| POST | `/auth/register` | Нет | Регистрация |
| POST | `/auth/login` | Нет | Получение JWT |
| GET | `/auth/me` | Да | Текущий пользователь |

Регистрация принимает `email` и `password` (не менее 8 символов). Вход принимает `username` (email) и `password` в формате `application/x-www-form-urlencoded`.

Пример регистрации:
```json
{"email":"demo@example.com","password":"DemoPass123"}
```

## 2. Кредитные продукты

| Метод | Путь | Авторизация | Назначение |
|---|---|---|---|
| GET | `/products` | Нет | Список активных продуктов |
| GET | `/products/{id}` | Нет | Детали продукта |

Основные поля продукта: `name`, `bank_name`, `interest_rate`, `min_amount`, `max_amount`, `min_term_months`, `max_term_months`, `commission_rate`, `commission_amount`, `description`, `additional_conditions`, `supported_purposes`, `min_business_age_months`, `requires_collateral`, `is_active`.

## 3. Калькулятор

| Метод | Путь | Авторизация | Назначение |
|---|---|---|---|
| POST | `/calculator/calculate` | Нет | Расчёт по продукту |
| POST | `/calculator/compare` | Нет | Сравнение продуктов |

`/calculator/calculate` принимает `product_id`, `amount`, `term_months`. В ответе ожидаются `monthly_payment`, `total_payment`, `overpayment`, `commission`, `disclaimer`.

`/calculator/compare` принимает `amount`, `term_months` и возвращает подходящие по диапазонам продукты с сортировкой по общей сумме платежей.

## 4. Заявки

| Метод | Путь | Авторизация | Назначение |
|---|---|---|---|
| POST | `/applications` | Да | Создать черновик |
| GET | `/applications` | Да | Список собственных заявок |
| GET | `/applications/{id}` | Да | Получить свою заявку |
| PATCH | `/applications/{id}` | Да | Изменить черновик |
| POST | `/applications/{id}/submit` | Да | Отправить заявку |
| GET | `/applications/{id}/history` | Да | История статусов |

При создании заявки используются поля `credit_product_id`, `amount`, `term_months`, `purpose`, `monthly_income`, `employment` (точный набор и обязательность нужно сверить с OpenAPI).

При отправке backend проверяет статус `draft`, доступность продукта и диапазоны суммы/срока, рассчитывает платёжные показатели, записывает предварительный результат и меняет статус на `submitted`.

Предварительная оценка:
- `likely_eligible` — платёж не превышает 40% указанного дохода;
- `high_debt_burden` — платёж превышает 40% указанного дохода.

Это демонстрационная эвристика, а не решение банка.

## 5. Обработка заявок сотрудником

Требуется роль `staff` или `admin`.

| Метод | Путь | Переход |
|---|---|---|
| GET | `/applications/staff` | Просмотр всех заявок |
| POST | `/applications/{id}/check` | `submitted` → `checking` |
| POST | `/applications/{id}/request-info` | `submitted`/`checking` → `needs_info` |
| POST | `/applications/{id}/offer-alternative` | `submitted`/`checking` → `alternative_offer` |
| POST | `/applications/{id}/approve` | `submitted` → `approved` |
| POST | `/applications/{id}/reject` | `submitted` → `rejected` |

Отклонение принимает тело с `reason` (минимум 3 символа, согласно предоставленному описанию). В предоставленном документе для `/approve` и некоторых других операций не указаны точные схемы тела; их нужно смотреть в `/docs`.

## 6. Профиль бизнеса

| Метод | Путь | Авторизация | Назначение |
|---|---|---|---|
| GET | `/business-profile` | Да | Получить профиль |
| PUT | `/business-profile` | Да | Создать или обновить профиль |

Поля: `business_name`, `legal_form` (`IP` или `OOO`), `industry`, `region`, `business_start_date`, `monthly_revenue`. Для отсутствующего профиля `GET` возвращает 404 согласно описанию.

## 7. Рекомендации

| Метод | Путь | Авторизация | Назначение |
|---|---|---|---|
| POST | `/recommendations` | Да | Создать подбор |
| GET | `/recommendations/{id}` | Да | Получить сохранённый подбор |

`POST /recommendations` принимает `requested_amount`, `term_months`, `purpose`, необязательные `monthly_revenue` и `business_age_months`.

Подбор фильтрует неактивные продукты и продукты, не соответствующие сумме, сроку, цели или минимальному возрасту бизнеса. Элементы результата содержат `product_id`, `match_score`, `estimated_monthly_payment`, `reasons`. Оценка описана как взвешенная: сумма — 40%, срок — 30%, доход — 20%, возраст бизнеса — 10%.

## 8. Полный список путей

| Метод | Путь |
|---|---|
| POST | `/auth/register` |
| POST | `/auth/login` |
| GET | `/auth/me` |
| GET | `/products` |
| GET | `/products/{id}` |
| POST | `/calculator/calculate` |
| POST | `/calculator/compare` |
| POST | `/applications` |
| GET | `/applications` |
| GET | `/applications/{id}` |
| PATCH | `/applications/{id}` |
| POST | `/applications/{id}/submit` |
| GET | `/applications/{id}/history` |
| GET | `/applications/staff` |
| POST | `/applications/{id}/check` |
| POST | `/applications/{id}/request-info` |
| POST | `/applications/{id}/offer-alternative` |
| POST | `/applications/{id}/approve` |
| POST | `/applications/{id}/reject` |
| GET | `/business-profile` |
| PUT | `/business-profile` |
| POST | `/recommendations` |
| GET | `/recommendations/{id}` |

