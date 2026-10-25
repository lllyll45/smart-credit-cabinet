# Smart Credit Cabinet

Веб-приложение для подбора кредитных предложений и подачи заявок на кредитование малого бизнеса.

Команда: 3 человека — 2 backend-разработчика, 1 frontend-разработчик.

## Что сделано

### Backend

- **FastAPI** + **PostgreSQL** + **SQLAlchemy** + **Alembic**
- **7 таблиц**: `users`, `credit_products`, `credit_applications`, `application_history`, `business_profiles`, `recommendations`, `recommendation_items`
- **JWT-авторизация** (Argon2 для паролей)
- **Роли**: `client`, `staff`, `admin`
- **84 автотеста** (`pytest -v`) — все проходят
- **Docker Compose** — Postgres + backend поднимаются одной командой

### Эндпоинты (все работают)

**Аккаунт:**
- `POST /api/v1/auth/register` — регистрация
- `POST /api/v1/auth/login` — вход
- `GET /api/v1/auth/me` — текущий пользователь

**Каталог продуктов:**
- `GET /api/v1/products` — список активных
- `GET /api/v1/products/{id}` — детали

**Калькулятор:**
- `POST /api/v1/calculator/calculate` — расчёт по продукту
- `POST /api/v1/calculator/compare` — сравнение подходящих

**Кредитные заявки:**
- `POST /api/v1/applications` — создать черновик
- `GET /api/v1/applications` — свои заявки
- `GET /api/v1/applications/{id}` — заявка по ID
- `PATCH /api/v1/applications/{id}` — изменить черновик
- `POST /api/v1/applications/{id}/submit` — отправить (расчёт + preliminary_result)
- `GET /api/v1/applications/{id}/history` — история статусов

**Staff-эндпоинты (роль `staff`/`admin`):**
- `GET /api/v1/applications/staff` — все заявки
- `POST /api/v1/applications/{id}/check` — `submitted → checking`
- `POST /api/v1/applications/{id}/request-info` — `submitted/checking → needs_info`
- `POST /api/v1/applications/{id}/offer-alternative` — `submitted/checking → alternative_offer`
- `POST /api/v1/applications/{id}/approve` — `submitted → approved`
- `POST /api/v1/applications/{id}/reject` — `submitted → rejected` (с причиной)

**Профиль бизнеса:**
- `GET /api/v1/business-profile` — получить (404 если нет)
- `PUT /api/v1/business-profile` — создать или обновить (upsert)

**Рекомендации:**
- `POST /api/v1/recommendations` — подобрать и сохранить
- `GET /api/v1/recommendations/{id}` — получить (404 для чужого)

### Статусы заявки
