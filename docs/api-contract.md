# API Contract — Smart Credit Cabinet

## Общие правила
- Base URL: `http://localhost:8000`; префикс API: `/api/v1`.
- Запросы и ответы — JSON; поля JSON в `snake_case`.
- Идентификаторы — UUID. Дата/время — ISO 8601 с часовым поясом; серверное время хранить в UTC.
- Денежные значения передаются в рублях; на backend использовать `Decimal` и SQL `NUMERIC`, не `float`.
- Защищённые методы требуют `Authorization: Bearer <access_token>`.
- Владелец определяется по токену, не по `user_id` из тела запроса.
- Статус заявки меняется только сервером через предусмотренные действия.

## Формат ошибки
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Проверьте переданные данные",
    "details": [{"field": "amount", "message": "Сумма должна быть положительной"}]
  }
}
```
`details` может быть пустым массивом. Ошибки FastAPI `422` нужно преобразовать к этому формату.

HTTP-коды: `200` — успех; `201` — ресурс создан; `204` — успех без тела; `400` — некорректный запрос; `401` — не авторизован; `403` — запрещено; `404` — не найдено/нет доступа; `409` — конфликт состояния; `422` — ошибка валидации; `500` — внутренняя ошибка.

## Статусы заявок
`DRAFT`, `SUBMITTED`, `CHECKING`, `NEEDS_INFO`, `APPROVED`, `REJECTED`, `ALTERNATIVE_OFFER`.
`APPROVED` и `REJECTED` в MVP — результаты демонстрационного алгоритма, а не решение реального банка.

## Авторизация

### `POST /api/v1/auth/register`
Request:
```json
{"email":"owner@example.com","password":"example-password"}
```
Response `201`:
```json
{"id":"8b5d14f0-97c7-4e28-9a3e-38f26b5a0200","email":"owner@example.com","created_at":"2026-10-22T10:00:00Z"}
```
Пароль не возвращается; хранится только безопасный хеш.

### `POST /api/v1/auth/login`
Request:
```json
{"email":"owner@example.com","password":"example-password"}
```
Response `200`:
```json
{"access_token":"<jwt-token>","token_type":"bearer"}
```

### `GET /api/v1/auth/me`
Требует JWT. Response `200`:
```json
{"id":"8b5d14f0-97c7-4e28-9a3e-38f26b5a0200","email":"owner@example.com"}
```

## Профиль бизнеса

### `GET /api/v1/business-profile`
Возвращает профиль текущего пользователя; если профиль отсутствует — `404`.
Response `200`:
```json
{
  "id":"c11ac55a-5aaf-4e7a-9e20-03c8fbcf53f2",
  "business_name":"ООО Ромашка",
  "legal_form":"OOO",
  "industry":"Торговля",
  "region":"Республика Башкортостан",
  "business_start_date":"2022-05-01",
  "monthly_revenue":850000,
  "created_at":"2026-10-22T10:00:00Z",
  "updated_at":"2026-10-22T10:00:00Z"
}
```

### `PUT /api/v1/business-profile`
Создаёт или полностью обновляет профиль.
Request:
```json
{
  "business_name":"ООО Ромашка",
  "legal_form":"OOO",
  "industry":"Торговля",
  "region":"Республика Башкортостан",
  "business_start_date":"2022-05-01",
  "monthly_revenue":850000
}
```
Response `200`: объект профиля, как в `GET`. `legal_form`: `IP` или `OOO`.

## Кредитные продукты

### `GET /api/v1/products`
Публичный список активных продуктов.
Response `200`:
```json
{
  "items":[{
    "id":"e59e94f7-2cbb-46d5-ae83-0801c88b4d90",
    "name":"Оборотный кредит",
    "description":"Финансирование текущих расходов бизнеса",
    "min_amount":100000,
    "max_amount":5000000,
    "min_term_months":3,
    "max_term_months":36,
    "interest_rate_min":15.5,
    "interest_rate_max":24.0,
    "min_business_age_months":6,
    "supported_purposes":["WORKING_CAPITAL","EQUIPMENT"],
    "requires_collateral":false
  }],
  "total":1
}
```

### `GET /api/v1/products/{product_id}`
Возвращает объект продукта. Для отсутствующего или неактивного продукта — `404`.
Суммы — рубли; срок — месяцы; процентные ставки — годовые проценты.

## Рекомендации

### `POST /api/v1/recommendations`
Требует JWT; создаёт и сохраняет результат подбора.
Request:
```json
{
  "requested_amount":750000,
  "term_months":24,
  "purpose":"WORKING_CAPITAL",
  "monthly_revenue":850000,
  "business_age_months":30
}
```
Response `201`:
```json
{
  "id":"95e75df8-1d7c-4b83-8e52-a5eb62fd78f9",
  "requested_amount":750000,
  "term_months":24,
  "purpose":"WORKING_CAPITAL",
  "items":[{
    "product":{"id":"e59e94f7-2cbb-46d5-ae83-0801c88b4d90","name":"Оборотный кредит"},
    "match_score":88,
    "estimated_monthly_payment":37000,
    "reasons":["Сумма входит в диапазон продукта","Срок соответствует условиям","Цель кредита поддерживается"]
  }],
  "created_at":"2026-10-22T10:00:00Z"
}
```
`match_score` — условная оценка соответствия 0–100, не вероятность одобрения. Платёж ориентировочный и не является банковской офертой.

### `GET /api/v1/recommendations/{recommendation_id}`
Возвращает сохранённый подбор текущего пользователя; чужой или отсутствующий ресурс — `404`.

## Заявки

### `POST /api/v1/applications`
Создаёт черновик; требует JWT.
Request:
```json
{
  "product_id":"e59e94f7-2cbb-46d5-ae83-0801c88b4d90",
  "amount":750000,
  "term_months":24,
  "purpose":"WORKING_CAPITAL",
  "recommendation_item_id":null
}
```
Response `201`:
```json
{
  "id":"6d22283a-bd67-4f62-9402-60d3ac4f5d5e",
  "product_id":"e59e94f7-2cbb-46d5-ae83-0801c88b4d90",
  "product_name":"Оборотный кредит",
  "amount":750000,
  "term_months":24,
  "purpose":"WORKING_CAPITAL",
  "status":"DRAFT",
  "created_at":"2026-10-22T10:00:00Z",
  "updated_at":"2026-10-22T10:00:00Z",
  "submitted_at":null
}
```

### `GET /api/v1/applications`
Только заявки текущего пользователя.
Response `200`:
```json
{"items":[{"id":"6d22283a-bd67-4f62-9402-60d3ac4f5d5e","product_id":"e59e94f7-2cbb-46d5-ae83-0801c88b4d90","product_name":"Оборотный кредит","amount":750000,"term_months":24,"purpose":"WORKING_CAPITAL","status":"DRAFT","created_at":"2026-10-22T10:00:00Z","updated_at":"2026-10-22T10:00:00Z","submitted_at":null}],"total":1}
```

### `GET /api/v1/applications/{application_id}`
Возвращает заявку текущего пользователя в формате объекта заявки из `POST /applications`.

### `PATCH /api/v1/applications/{application_id}`
Редактирует только `DRAFT`. Все поля необязательны.
Request:
```json
{"amount":900000,"term_months":30}
```
Response `200`: обновлённая заявка. Для заявки в другом статусе — `409`.

### `POST /api/v1/applications/{application_id}/submit`
Отправляет черновик на обработку; тело пустое.
Response `200`:
```json
{"id":"6d22283a-bd67-4f62-9402-60d3ac4f5d5e","status":"SUBMITTED","submitted_at":"2026-10-22T10:05:00Z"}
```
Повторная отправка заявки не в `DRAFT` — `409`; некорректные данные — `422`.

## Решение и история

### `GET /api/v1/applications/{application_id}/decision`
Response `200`:
```json
{
  "application_id":"6d22283a-bd67-4f62-9402-60d3ac4f5d5e",
  "result":"ALTERNATIVE_OFFER",
  "score":72,
  "reason":"Найден продукт, лучше соответствующий указанному сроку",
  "alternative_product_id":"e59e94f7-2cbb-46d5-ae83-0801c88b4d90",
  "created_at":"2026-10-22T10:10:00Z"
}
```
`result`: `APPROVED`, `REJECTED` или `ALTERNATIVE_OFFER`. Если решения ещё нет, единообразно реализовать `404 DECISION_NOT_FOUND` либо `200` с `decision: null` и отразить это в OpenAPI.

### `GET /api/v1/applications/{application_id}/history`
Response `200`:
```json
{
  "items":[
    {"id":"2b5af38e-7ad8-4cc1-9bb6-a4bb07e7f7f4","old_status":null,"new_status":"DRAFT","comment":"Заявка создана","created_at":"2026-10-22T10:00:00Z"},
    {"id":"5b29a4c2-bb8e-4bde-9f84-9fb4d83f34c7","old_status":"DRAFT","new_status":"SUBMITTED","comment":"Заявка отправлена пользователем","created_at":"2026-10-22T10:05:00Z"}
  ],
  "total":2
}
```

## Соглашения реализации
1. В ответах не возвращать пароль, хеш пароля, секреты и stack trace.
2. Списки возвращают `{ "items": [], "total": 0 }`.
3. Все запросы к заявкам проверяют владельца.
4. Контракт сверяется с автоматически генерируемой документацией FastAPI `/docs`; при изменениях обновлять этот документ.
