# API Smart Credit Cabinet

Базовый префикс: `/api/v1`. Защищённые эндпоинты требуют `Authorization: Bearer <token>`.

## 1. Аккаунт и авторизация

| Метод | Путь | Авторизация | Назначение |
|---|---|---|---|
| POST | `/auth/register` | Нет | Регистрация |
| POST | `/auth/login` | Нет | Получение JWT |
| GET | `/auth/me` | Да | Текущий пользователь |

Регистрация принимает `email` (EmailStr) и `password` (8–128 символов). Вход принимает `username` (email) и `password` в формате `application/x-www-form-urlencoded`.

Пример регистрации:
```json
{"email":"demo@example.com","password":"DemoPass123"}
```

Ответ логина:
```json
{"access_token":"<jwt>","token_type":"bearer"}
```

## 2. Кредитные продукты

| Метод | Путь | Авторизация | Назначение |
|---|---|---|---|
| GET | `/products` | Нет | Список активных продуктов |
| GET | `/products/{id}` | Нет | Детали продукта (404 для неактивного) |

Поля продукта: `id`, `name`, `bank_name`, `interest_rate`, `min_amount`, `max_amount`, `min_term_months`, `max_term_months`, `commission_rate`, `commission_amount`, `description`, `additional_conditions`, `supported_purposes`, `min_business_age_months`, `requires_collateral`, `is_active`, `created_at`, `updated_at`.

## 3. Калькулятор

| Метод | Путь | Авторизация | Назначение |
|---|---|---|---|
| POST | `/calculator/calculate` | Нет | Расчёт по продукту |
| POST | `/calculator/compare` | Нет | Сравнение продуктов |

`/calculator/calculate`:
```json
{"product_id": 1, "amount": "120000", "term_months": 12}
```
Ответ: `product_id`, `product_name`, `bank_name`, `interest_rate`, `amount`, `term_months`, `monthly_payment`, `total_payment`, `overpayment`, `commission`, `disclaimer`.

Ошибки: `404` — продукт не найден/неактивен; `422` — сумма или срок вне диапазона.

`/calculator/compare`:
```json
{"amount": "120000", "term_months": 12}
```
Ответ: `amount`, `term_months`, `products` (отсортированы по `total_payment` по возрастанию).

## 4. Заявки

| Метод | Путь | Авторизация | Назначение |
|---|---|---|---|
| POST | `/applications` | Да | Создать черновик |
| GET | `/applications` | Да | Список собственных заявок |
| GET | `/applications/{id}` | Да | Получить свою заявку |
| PATCH | `/applications/{id}` | Да | Изменить черновик |
| POST | `/applications/{id}/submit` | Да | Отправить заявку |
| GET | `/applications/{id}/history` | Да | История статусов |

Тело создания:
```json
{
  "credit_product_id": 1,
  "amount": "100000",
  "term_months": 12,
  "purpose": "Тестовая цель",
  "monthly_income": "50000",
  "employment": "ИП"
}
```

Статус после создания: `draft`.

Ошибки создания: `422` — продукт не найден/неактивен, сумма или срок вне лимита, доход ≤ 0.

При `submit`:
1. Проверка статуса `draft`.
2. Проверка продукта (активен, сумма и срок в лимитах).
3. Расчёт `monthly_payment`, `total_payment`, `overpayment`.
4. Установка `preliminary_result`:
   - `likely_eligible` — платёж ≤ 40% дохода;
   - `high_debt_burden` — платёж > 40% дохода.
5. Статус → `submitted`, запись в историю.

Ошибки: `404` — заявка не найдена/чужая; `409` — не `draft`; `422` — нет продукта/данные не проходят.

`/history` возвращает массив записей: `id`, `application_id`, `old_status`, `new_status`, `comment`, `created_at` (хронологический порядок).

## 5. Обработка заявок сотрудником

Требуется роль `staff` или `admin` (иначе `403`).

| Метод | Путь | Переход |
|---|---|---|
| GET | `/applications/staff` | Просмотр всех заявок |
| POST | `/applications/{id}/check` | `submitted` → `checking` |
| POST | `/applications/{id}/request-info` | `submitted`/`checking` → `needs_info` |
| POST | `/applications/{id}/offer-alternative` | `submitted`/`checking` → `alternative_offer` |
| POST | `/applications/{id}/approve` | `submitted` → `approved` |
| POST | `/applications/{id}/reject` | `submitted` → `rejected` |

`/reject` принимает:
```json
{"reason": "Недостаточный доход"}
```
`reason` — минимум 3 символа (после `.strip()`), иначе `422`. Причина сохраняется в `decision_comment` и в истории.

Каждый переход записывает событие в `application_history`.

## 6. Профиль бизнеса

| Метод | Путь | Авторизация | Назначение |
|---|---|---|---|
| GET | `/business-profile` | Да | Получить профиль (404 если нет) |
| PUT | `/business-profile` | Да | Создать или обновить (upsert) |

Тело `PUT`:
```json
{
  "business_name": "ООО Ромашка",
  "legal_form": "OOO",
  "industry": "Торговля",
  "region": "Республика Башкортостан",
  "business_start_date": "2022-05-01",
  "monthly_revenue": "850000.00"
}
```

`legal_form` — строго `IP` или `OOO` (иначе `422`). `business_name` — 1..255. `monthly_revenue` — ≥ 0.

## 7. Рекомендации

| Метод | Путь | Авторизация | Назначение |
|---|---|---|---|
| POST | `/recommendations` | Да | Создать подбор |
| GET | `/recommendations/{id}` | Да | Получить сохранённый подбор (404 для чужого) |

Тело `POST`:
```json
{
  "requested_amount": "200000",
  "term_months": 18,
  "purpose": "working_capital",
  "monthly_revenue": "200000",
  "business_age_months": 24
}
```

Ответ:
```json
{
  "id": 1,
  "user_id": 1,
  "requested_amount": "200000.00",
  "term_months": 18,
  "purpose": "working_capital",
  "monthly_revenue": "200000.00",
  "business_age_months": 24,
  "created_at": "...",
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "match_score": "92.00",
      "estimated_monthly_payment": "11110.40",
      "reasons": ["Сумма входит в диапазон продукта", "..."]
    }
  ]
}
```

Фильтрация:
- продукт активен;
- сумма и срок в диапазоне продукта;
- `purpose` ∈ `supported_purposes` (если список не пуст);
- `business_age_months` ≥ `min_business_age_months` (если задано).

`match_score` (0..100) — взвешенный: сумма 40%, срок 30%, доход 20%, возраст бизнеса 10%.

## 8. Сводная таблица

| Метод | Путь | Авторизация |
|---|---|---|
| POST | `/auth/register` | Нет |
| POST | `/auth/login` | Нет |
| GET | `/auth/me` | Да |
| GET | `/products` | Нет |
| GET | `/products/{id}` | Нет |
| POST | `/calculator/calculate` | Нет |
| POST | `/calculator/compare` | Нет |
| POST | `/applications` | Да |
| GET | `/applications` | Да |
| GET | `/applications/{id}` | Да |
| PATCH | `/applications/{id}` | Да |
| POST | `/applications/{id}/submit` | Да |
| GET | `/applications/{id}/history` | Да |
| GET | `/applications/staff` | staff/admin |
| POST | `/applications/{id}/check` | staff/admin |
| POST | `/applications/{id}/request-info` | staff/admin |
| POST | `/applications/{id}/offer-alternative` | staff/admin |
| POST | `/applications/{id}/approve` | staff/admin |
| POST | `/applications/{id}/reject` | staff/admin |
| GET | `/business-profile` | Да |
| PUT | `/business-profile` | Да |
| POST | `/recommendations` | Да |
| GET | `/recommendations/{id}` | Да |
