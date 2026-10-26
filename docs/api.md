# API Smart Credit Cabinet

## Общая информация

**Название:** Smart Credit Cabinet  
**Версия API:** `0.1.0`  
**Базовый префикс:** `/api/v1`  
**Swagger UI:** `http://localhost:8000/docs`  
**OpenAPI JSON:** `http://localhost:8000/openapi.json`

Защищённые эндпоинты требуют JWT-токен в заголовке:

```http
Authorization: Bearer <token>
```

Формат JSON используется для большинства запросов. Авторизация через логин выполняется с типом содержимого `application/x-www-form-urlencoded`.

## 1. Аккаунт и авторизация

| Метод | Путь | Авторизация | Назначение |
|---|---|---|---|
| POST | `/auth/register` | Нет | Регистрация пользователя |
| POST | `/auth/login` | Нет | Получение JWT-токена |
| GET | `/auth/me` | Да | Получение данных текущего пользователя |

### Регистрация

Эндпоинт: `POST /api/v1/auth/register`

Тело запроса:

```json
{
  "email": "demo@example.com",
  "password": "DemoPass123"
}
```

Поля:
- `email` — корректный адрес электронной почты.
- `password` — пароль длиной от 8 до 128 символов.

Успешный ответ — `201 Created`. Возвращаются `id`, `email` и `created_at`.

### Вход

Эндпоинт: `POST /api/v1/auth/login`

Тип содержимого: `application/x-www-form-urlencoded`.

Поля формы:
- `username` — email пользователя;
- `password` — пароль.

Пример полей формы:

```text
username=demo@example.com
password=DemoPass123
```

Ответ:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

Полученный `access_token` используется для обращения к защищённым эндпоинтам.

### Текущий пользователь

Эндпоинт: `GET /api/v1/auth/me`

Требует авторизации. Возвращает данные текущего пользователя; точная схема ответа в OpenAPI не определена.

## 2. Кредитные продукты

| Метод | Путь | Авторизация | Назначение |
|---|---|---|---|
| GET | `/products` | Нет | Получение списка продуктов |
| GET | `/products/{product_id}` | Нет | Получение продукта по ID |

### Основные поля ответа

Согласно OpenAPI, схема `CreditProductResponse` включает:

- `id` — идентификатор;
- `name` — название продукта;
- `bank_name` — название банка;
- `interest_rate` — процентная ставка;
- `min_amount`, `max_amount` — допустимая сумма кредита;
- `min_term_months`, `max_term_months` — минимальный и максимальный срок;
- `commission_rate`, `commission_amount` — параметры комиссии, если заданы;
- `is_active` — признак активности;
- `created_at`, `updated_at` — даты создания и обновления.

Хотя модель продукта может содержать описание, допустимые цели, требования к возрасту бизнеса и обеспечению, эти поля не включены в опубликованную схему `CreditProductResponse`. Если они должны возвращаться клиенту, необходимо дополнить схему и проверить фактический ответ API.

## 3. Кредитный калькулятор

| Метод | Путь | Авторизация | Назначение |
|---|---|---|---|
| POST | `/calculator/calculate` | Нет | Расчёт кредита по выбранному продукту |
| POST | `/calculator/compare` | Нет | Сравнение кредитных продуктов |

### Расчёт кредита

Эндпоинт: `POST /api/v1/calculator/calculate`

Тело запроса:

```json
{
  "product_id": 1,
  "amount": "120000",
  "term_months": 12
}
```

Обязательные поля:
- `product_id` — идентификатор продукта;
- `amount` — сумма кредита больше нуля;
- `term_months` — срок в месяцах больше нуля.

В ответе предусмотрены:
- `product_id`, `product_name`, `bank_name`;
- `interest_rate`, `amount`, `term_months`;
- `monthly_payment` — ежемесячный платёж;
- `total_payment` — общая сумма выплат;
- `overpayment` — переплата;
- `commission` — комиссия;
- `disclaimer` — предупреждение о предварительном характере расчёта.

### Сравнение продуктов

Эндпоинт: `POST /api/v1/calculator/compare`

Тело запроса:

```json
{
  "amount": "120000",
  "term_months": 12
}
```

В ответе возвращаются сумма, срок и массив рассчитанных продуктов. Правила фильтрации и сортировки необходимо подтверждать реализацией калькулятора: OpenAPI описывает структуру ответа, но не фиксирует алгоритм сравнения.

## 4. Профиль бизнеса

| Метод | Путь | Авторизация | Назначение |
|---|---|---|---|
| GET | `/business-profile` | Да | Получение профиля текущего пользователя |
| PUT | `/business-profile` | Да | Создание или полное обновление профиля |

### Создание или обновление профиля

Эндпоинт: `PUT /api/v1/business-profile`

Пример запроса:

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

Поля:
- `business_name` — название бизнеса, от 1 до 255 символов;
- `legal_form` — организационно-правовая форма: `IP` или `OOO`;
- `industry` — отрасль;
- `region` — регион;
- `business_start_date` — дата начала деятельности в формате `YYYY-MM-DD`;
- `monthly_revenue` — среднемесячная выручка, неотрицательное число.

Обязательны только `business_name` и `legal_form`; остальные поля могут быть `null` или отсутствовать.

Успешный ответ содержит `BusinessProfileResponse`, включая `id`, `user_id`, данные бизнеса и временные метки.

**Важно:** профиль бизнеса связан с текущим авторизованным пользователем. Перед созданием заявки следует убедиться, что профиль заполнен, если этого требует бизнес-логика приложения.

## 5. Кредитные заявки

| Метод | Путь | Авторизация | Назначение |
|---|---|---|---|
| POST | `/applications` | Да | Создание черновика |
| GET | `/applications` | Да | Список заявок текущего пользователя |
| GET | `/applications/{application_id}` | Да | Получение заявки |
| PATCH | `/applications/{application_id}` | Да | Изменение черновика |
| POST | `/applications/{application_id}/submit` | Да | Отправка на рассмотрение |
| GET | `/applications/{application_id}/history` | Да | История изменений статуса |

### Создание заявки

Эндпоинт: `POST /api/v1/applications`

Тело запроса:

```json
{
  "credit_product_id": 1,
  "amount": "100000",
  "term_months": 12,
  "purpose": "working_capital"
}
```

Все четыре поля обязательны:

- `credit_product_id` — идентификатор кредитного продукта;
- `amount` — сумма больше нуля;
- `term_months` — срок больше нуля;
- `purpose` — цель кредитования длиной от 3 до 255 символов.

По описанию эндпоинта создаётся черновик заявки с использованием профиля бизнеса текущего пользователя.

Поля `monthly_income` и `employment` не входят в опубликованную схему `CreditApplicationCreate`; передавать их как обязательные поля не требуется по текущему OpenAPI-контракту.

Успешный ответ — `201 Created`, тело соответствует `CreditApplicationResponse`.

### Изменение черновика

Эндпоинт: `PATCH /api/v1/applications/{application_id}`

Позволяет передать поля для изменения:
- `credit_product_id`;
- `amount`;
- `term_months`;
- `purpose`.

Поля необязательны и могут быть `null` согласно схеме OpenAPI. Эндпоинт описан как изменение заявки, пока она находится в статусе черновика.

### Отправка заявки

Эндпоинт: `POST /api/v1/applications/{application_id}/submit`

Описание API указывает, что при отправке рассчитываются платежи и заявка передаётся сотруднику на рассмотрение.

Предусмотренные в схеме заявки поля результата:
- `monthly_payment`;
- `total_payment`;
- `overpayment`;
- `preliminary_result`;
- `status`.


### История заявки

Эндпоинт: `GET /api/v1/applications/{application_id}/history`

Возвращает массив записей `ApplicationHistoryResponse`:

- `id`;
- `application_id`;
- `old_status`;
- `new_status`;
- `comment`;
- `created_at`.

## 6. Обработка заявок сотрудником

Для этих операций предусмотрены отдельные эндпоинты. Согласно назначению API, доступ к ним должен быть у сотрудников банка.

| Метод | Путь | Назначение |
|---|---|---|
| GET | `/applications/staff` | Получение списка заявок для сотрудников |
| POST | `/applications/{application_id}/check` | Перевод заявки на проверку |
| POST | `/applications/{application_id}/request-info` | Запрос дополнительной информации |
| POST | `/applications/{application_id}/offer-alternative` | Предложение альтернативных условий |
| POST | `/applications/{application_id}/approve` | Одобрение заявки |
| POST | `/applications/{application_id}/reject` | Отклонение заявки |

### Отклонение заявки

Эндпоинт: `POST /api/v1/applications/{application_id}/reject`

Тело запроса:

```json
{
  "reason": "Недостаточный доход"
}
```

Поле `reason` обязательно, длина — от 3 до 1000 символов.



## 7. Рекомендации по кредитным продуктам

| Метод | Путь | Авторизация | Назначение |
|---|---|---|---|
| POST | `/recommendations` | Да | Создание и сохранение результата подбора |
| GET | `/recommendations/{recommendation_id}` | Да | Получение сохранённого подбора |

### Создание рекомендации

Эндпоинт: `POST /api/v1/recommendations`

Пример запроса:

```json
{
  "requested_amount": "200000",
  "term_months": 18,
  "purpose": "working_capital",
  "monthly_revenue": "200000",
  "business_age_months": 24
}
```

Обязательные поля:
- `requested_amount` — запрашиваемая сумма больше нуля;
- `term_months` — срок больше нуля;
- `purpose` — цель кредитования, от 1 до 100 символов.

Необязательные поля:
- `monthly_revenue` — среднемесячная выручка;
- `business_age_months` — возраст бизнеса в месяцах.

Успешный ответ — `201 Created`. Он содержит идентификатор рекомендации, исходные параметры, дату создания и массив элементов результата.

Элемент рекомендации включает:
- `product_id`;
- `match_score`;
- `estimated_monthly_payment`;
- `reasons` — список объяснений соответствия продукта.

### Получение рекомендации

Эндпоинт: `GET /api/v1/recommendations/{recommendation_id}`

Возвращает сохранённую рекомендацию. Согласно описанию эндпоинта, она относится к текущему пользователю.


## 8. Служебные эндпоинты

| Метод | Путь | Авторизация | Назначение |
|---|---|---|---|
| GET | `/` | Нет | Корневой эндпоинт |
| GET | `/health` | Нет | Проверка доступности сервиса |

## 9. Полный список эндпоинтов

Все пути ниже указаны относительно префикса `/api/v1`.

| Метод | Путь |
|---|---|
| POST | `/auth/register` |
| POST | `/auth/login` |
| GET | `/auth/me` |
| GET | `/products` |
| GET | `/products/{product_id}` |
| POST | `/calculator/calculate` |
| POST | `/calculator/compare` |
| GET | `/business-profile` |
| PUT | `/business-profile` |
| POST | `/applications` |
| GET | `/applications` |
| GET | `/applications/{application_id}` |
| PATCH | `/applications/{application_id}` |
| POST | `/applications/{application_id}/submit` |
| GET | `/applications/{application_id}/history` |
| GET | `/applications/staff` |
| POST | `/applications/{application_id}/check` |
| POST | `/applications/{application_id}/request-info` |
| POST | `/applications/{application_id}/offer-alternative` |
| POST | `/applications/{application_id}/approve` |
| POST | `/applications/{application_id}/reject` |
| POST | `/recommendations` |
| GET | `/recommendations/{recommendation_id}` |
| GET | `/` |
| GET | `/health` |

## 10. Проверка API

Для проверки запросов используйте Swagger UI:

`http://localhost:8000/docs`

Рекомендуемый порядок проверки пользовательского сценария:

1. Зарегистрировать пользователя или войти под тестовым аккаунтом.
2. Получить JWT-токен.
3. Выполнить авторизованный запрос к `/auth/me`.
4. Получить список кредитных продуктов.
5. Создать или обновить профиль бизнеса через `/business-profile`.
6. Создать заявку через `/applications`.
7. Отправить черновик на рассмотрение через `/applications/{application_id}/submit`.
8. Проверить заявку и историю её статусов.
9. Войти под аккаунтом сотрудника и проверить операции обработки заявок.

