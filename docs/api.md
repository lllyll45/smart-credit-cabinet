# API Smart Credit Cabinet

Базовый адрес: `/api/v1`. Документ соответствует текущей реализации backend (84 теста).

## 1. Аккаунт и авторизация

| Метод | Эндпоинт | Назначение |
|---|---|---|
| `POST` | `/auth/register` | Регистрация пользователя |
| `POST` | `/auth/login` | Вход (form-urlencoded) |
| `GET` | `/auth/me` | Данные текущего пользователя |

Регистрация принимает `email` и `password` (min 8 символов). Пароль хешируется (Argon2).

Вход принимает `username` (email) и `password`, возвращает JWT-токен.

`/auth/me` требует `Authorization: Bearer <token>`.

## 2. Каталог кредитных продуктов

| Метод | Эндпоинт | Назначение |
|---|---|---|
| `GET` | `/products` | Список активных продуктов |
| `GET` | `/products/{id}` | Детали продукта |

Поля продукта:
- `name`, `bank_name` — название и банк
- `interest_rate` — годовая ставка, %
- `min_amount`, `max_amount` — диапазон суммы
- `min_term_months`, `max_term_months` — диапазон срока
- `commission_rate` — комиссия в % (или `null`)
- `commission_amount` — фиксированная комиссия (или `null`)
- `description`, `additional_conditions` — описание и условия
- `supported_purposes` — список поддерживаемых целей (`working_capital`, `equipment` и т.д.)
- `min_business_age_months` — минимальный возраст бизнеса
- `requires_collateral` — требуется ли обеспечение
- `is_active` — доступность

## 3. Кредитный калькулятор

| Метод | Эндпоинт | Назначение |
|---|---|---|
| `POST` | `/calculator/calculate` | Расчёт по продукту |
| `POST` | `/calculator/compare` | Сравнение подходящих продуктов |

`/calculator/calculate` принимает `product_id`, `amount`, `term_months`. Возвращает `monthly_payment`, `total_payment`, `overpayment`, `commission`, `disclaimer` (расчёт предварительный).

`/calculator/compare` принимает `amount`, `term_months`. Возвращает список продуктов, подходящих по сумме и сроку, отсортированный по `total_payment`.

## 4. Кредитные заявки

| Метод | Эндпоинт | Назначение |
|---|---|---|
| `POST` | `/applications` | Создать черновик |
| `GET` | `/applications` | Заявки текущего пользователя |
| `GET` | `/applications/{id}` | Заявка по ID |
| `PATCH` | `/applications/{id}` | Изменить черновик |
| `POST` | `/applications/{id}/submit` | Отправить на рассмотрение |
| `GET` | `/applications/{id}/history` | История изменения статусов |

Все эндпоинты требуют авторизации. Пользователь видит только свои заявки.

### Статусы заявки
- `draft` — черновик, доступен для редактирования
- `submitted` — отправлена, только чтение
- `checking` — на проверке (staff)
- `needs_info` — требуется дополнительная информация (staff)
- `alternative_offer` — предложены альтернативные условия (staff)
- `approved` — одобрена (staff)
- `rejected` — отклонена (staff)

### Submit
При отправке backend:
1. Проверяет, что заявка в статусе `draft`.
2. Проверяет продукт (активен, сумма и срок в лимитах).
3. Рассчитывает `monthly_payment`, `total_payment`, `overpayment`.
4. Выставляет `preliminary_result`:
   - `likely_eligible` — платёж ≤ 40% дохода
   - `high_debt_burden` — платёж > 40% дохода
5. Ставит статус `submitted` и пишет запись в историю.

## 5. Staff-эндпоинты заявок

Требуют роль `staff` или `admin`.

| Метод | Эндпоинт | Назначение | Откуда → Куда |
|---|---|---|---|
| `GET` | `/applications/staff` | Все заявки для staff | — |
| `POST` | `/applications/{id}/check` | Начать проверку | submitted → checking |
| `POST` | `/applications/{id}/request-info` | Запросить информацию | submitted/checking → needs_info |
| `POST` | `/applications/{id}/offer-alternative` | Предложить альтернативу | submitted/checking → alternative_offer |
| `POST` | `/applications/{id}/approve` | Одобрить | submitted → approved |
| `POST` | `/applications/{id}/reject` | Отклонить (тело `{"reason": "..."}`, min 3 символа) | submitted → rejected |

Все переходы пишут запись в `ApplicationHistory`.

## 6. Профиль бизнеса

| Метод | Эндпоинт | Назначение |
|---|---|---|
| `GET` | `/business-profile` | Получить профиль (404, если нет) |
| `PUT` | `/business-profile` | Создать или обновить (upsert) |

Поля: `business_name` (1..255), `legal_form` (`IP` или `OOO`), `industry`, `region`, `business_start_date`, `monthly_revenue` (≥ 0).

## 7. Рекомендации

| Метод | Эндпоинт | Назначение |
|---|---|---|
| `POST` | `/recommendations` | Подобрать и сохранить |
| `GET` | `/recommendations/{id}` | Получить сохранённый подбор (404 для чужого) |

`POST /recommendations` принимает:
- `requested_amount` (> 0)
- `term_months` (1..360)
- `purpose` (1..100)
- `monthly_revenue` (опционально)
- `business_age_months` (опционально)

Возвращает `id`, параметры подбора и `items` — список продуктов с:
- `product_id`
- `match_score` (0..100, взвешенный: сумма 40%, срок 30%, доход 20%, возраст 10%)
- `estimated_monthly_payment`
- `reasons` — массив строк с объяснением

Фильтрация:
- цель должна быть в `supported_purposes` продукта (если список не пуст)
- возраст бизнеса ≥ `min_business_age_months` (если задано)
- сумма и срок в диапазоне продукта
- продукт активен

## 8. Сводная таблица

| Раздел | Метод и путь | Авторизация |
|---|---|---|
| Аккаунт | `POST /auth/register` | Нет |
| Аккаунт | `POST /auth/login` | Нет |
| Аккаунт | `GET /auth/me` | Да |
| Каталог | `GET /products` | Нет |
| Каталог | `GET /products/{id}` | Нет |
| Калькулятор | `POST /calculator/calculate` | Нет |
| Калькулятор | `POST /calculator/compare` | Нет |
| Заявки | `POST /applications` | Да |
| Заявки | `GET /applications` | Да |
| Заявки | `GET /applications/{id}` | Да |
| Заявки | `PATCH /applications/{id}` | Да |
| Заявки | `POST /applications/{id}/submit` | Да |
| Заявки | `GET /applications/{id}/history` | Да |
| Staff | `GET /applications/staff` | staff/admin |
| Staff | `POST /applications/{id}/check` | staff/admin |
| Staff | `POST /applications/{id}/request-info` | staff/admin |
| Staff | `POST /applications/{id}/offer-alternative` | staff/admin |
| Staff | `POST /applications/{id}/approve` | staff/admin |
| Staff | `POST /applications/{id}/reject` | staff/admin |
| Профиль | `GET /business-profile` | Да |
| Профиль | `PUT /business-profile` | Да |
| Рекомендации | `POST /recommendations` | Да |
| Рекомендации | `GET /recommendations/{id}` | Да |

Все защищённые эндпоинты требуют `Authorization: Bearer <token>`.