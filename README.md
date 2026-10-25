# Smart Credit Cabinet

Веб-приложение для подбора кредитных предложений и подачи заявок на кредитование малого бизнеса.

## Стек

- Python 3.13, FastAPI, PostgreSQL, SQLAlchemy, Alembic
- Pydantic, JWT (PyJWT), Argon2 (pwdlib)
- pytest (84 теста)
- Docker, Docker Compose
- Frontend: React, TypeScript, Vite (в разработке)

## Что сделано

### Backend

- 7 таблиц: `users`, `credit_products`, `credit_applications`, `application_history`, `business_profiles`, `recommendations`, `recommendation_items`
- JWT-авторизация, роли `client` / `staff` / `admin`
- 84 автотеста, все проходят
- Docker Compose: Postgres + backend одной командой

### Статусы заявки

`draft` → `submitted` → `checking` → `approved` / `rejected` / `needs_info` / `alternative_offer`

Каждый переход пишется в `application_history`.

### Подбор предложений

`POST /api/v1/recommendations` — взвешенный `match_score` (0..100):
- сумма в диапазоне — 40%
- срок в диапазоне — 30%
- доход — 20%
- возраст бизнеса — 10%

## Эндпоинты

### Аккаунт
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

### Каталог
- `GET /api/v1/products`
- `GET /api/v1/products/{id}`

### Калькулятор
- `POST /api/v1/calculator/calculate`
- `POST /api/v1/calculator/compare`

### Заявки
- `POST /api/v1/applications`
- `GET /api/v1/applications`
- `GET /api/v1/applications/{id}`
- `PATCH /api/v1/applications/{id}`
- `POST /api/v1/applications/{id}/submit`
- `GET /api/v1/applications/{id}/history`

### Staff (staff/admin)
- `GET /api/v1/applications/staff`
- `POST /api/v1/applications/{id}/check`
- `POST /api/v1/applications/{id}/request-info`
- `POST /api/v1/applications/{id}/offer-alternative`
- `POST /api/v1/applications/{id}/approve`
- `POST /api/v1/applications/{id}/reject`

### Профиль бизнеса
- `GET /api/v1/business-profile`
- `PUT /api/v1/business-profile`

### Рекомендации
- `POST /api/v1/recommendations`
- `GET /api/v1/recommendations/{id}`

## Тесты

84 теста (`pytest -v`), SQLite in-memory с `StaticPool`, `JSONType` (JSONB для Postgres / JSON для SQLite).

## Запуск

### Docker (рекомендуется)
docker compose up --build

Backend автоматически применяет миграции и заливает демо-продукты. API: http://127.0.0.1:8000, Swagger: http://127.0.0.1:8000/docs.

### Локально

См. [README-setup.md](README-setup.md).

## Документация

- [docs/architecture.md](docs/architecture.md) — архитектура
- [docs/data-model.md](docs/data-model.md) — 7 таблиц, миграции, match_score
- [docs/application-states.md](docs/application-states.md) — статусы заявки
- [docs/api.md](docs/api.md) — все эндпоинты

## Ветки

- `main` — стабильная версия
- `develop/backend-api`
- `develop/backend-db`
- `develop/frontend`

## Ограничения MVP

- `preliminary_result` (40% дохода) — демо-правило, не банковский скоринг
- Демо-продукты не являются реальными предложениями банков
- Решение `approved`/`rejected` принимает staff вручную
- Реальных платежей и передачи данных в банк нет
