# Smart Credit Cabinet — инструкция по запуску

## 1. Требования

- **Git**
- **Docker Desktop** (рекомендуется) — https://www.docker.com/products/docker-desktop/
- **Python 3.13** (если запуск без Docker)
- **PostgreSQL 18** (если запуск без Docker)
- **PowerShell** (Windows)

## 2. Клонирование

```powershell
git clone https://github.com/lllyll45/smart-credit-cabinet.git
cd smart-credit-cabinet
```

## 3. Запуск через Docker Compose (рекомендуется)

Самый простой способ. Поднимает PostgreSQL и backend одной командой.

### 3.1. Убедиться, что Docker Desktop запущен

Иконка кита в трее должна быть **зелёной**. Если нет — запустите Docker Desktop и подождите 30–60 секунд.

Проверка:

```
docker --version
docker compose version
```

Ожидаемо: `Docker version 29.x.x`, `Docker Compose version v2.x.x` (или новее).

### 3.2. Запустить

```
docker compose up --build
```

Что произойдёт:

1. Скачается `postgres:16-alpine` (~80 МБ).
2. Соберётся backend из `backend/Dockerfile` (~2–3 минуты).
3. Запустится Postgres на порту **5433** (снаружи).
4. Backend автоматически:

- применит миграции Alembic (`alembic upgrade head`);
- зальёт 3 демо-продукта (`scripts.seed_products`);
- запустит uvicorn на порту **8000**.

### 3.3. Проверить

В **другом** окне PowerShell:

```
curl.exe http://127.0.0.1:8000/health
curl.exe http://127.0.0.1:8000/api/v1/products
```

Ожидаемо:

- `/health` → `{"status":"ok"}`
- `/products` → JSON с 3 продуктами

Swagger: http://127.0.0.1:8000/docs

### 3.4. Остановить

В окне с `docker compose up` — `Ctrl+C`. Или:

```
docker compose down
```

Данные сохраняются в volume `postgres_data`. Удалить и данные:

```
docker compose down -v
```

## 4. Локальный запуск (без Docker)

### 4.1. Создать PostgreSQL-пользователя и БД

В `psql` под `postgres`:

```
CREATE USER smart_credit WITH PASSWORD 'YOUR_LOCAL_PASSWORD';
CREATE DATABASE smart_credit OWNER smart_credit;
```

Замените `YOUR_LOCAL_PASSWORD` на свой пароль.

### 4.2. Виртуальное окружение

```
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4.3. Настроить `.env`

Скопируйте `.env.example` из корня в `backend/.env`:

```
Copy-Item ..\.env.example .env
notepad .env
```

Заполните:

```
DATABASE_URL=postgresql+psycopg://smart_credit:YOUR_LOCAL_PASSWORD@localhost:5432/smart_credit
JWT_SECRET_KEY=ВАШ_СГЕНЕРИРОВАННЫЙ_КЛЮЧ
```

`JWT_SECRET_KEY` — сгенерируйте командой:

```
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

Файл `.env` не коммитится (в `.gitignore`).

### 4.4. Применить миграции

```
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Ожидаемо: цепочка `Running upgrade ...` до последней ревизии `c3d4e5f6a7b8`.

### 4.5. Залить демо-продукты

```
.\.venv\Scripts\python.exe -m scripts.seed_products
```

Ожидаемо: `Добавлено продуктов: 3`.

### 4.6. Запустить backend

```
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Swagger: http://127.0.0.1:8000/docs

### 4.7. Остановить

`Ctrl+C`.

## 5. Тесты

```
cd backend
.\.venv\Scripts\python.exe -m pytest -v
```

Ожидаемо: **84 passed, 1 warning**.

Тесты используют SQLite in-memory с `StaticPool`, PostgreSQL для тестов **не нужен**.

## 6. Проверить API вручную

### 6.1. Через Swagger (проще всего)

1. Откройте http://127.0.0.1:8000/docs
2. `POST /api/v1/auth/register` — создайте пользователя:

```
{"email": "demo@example.com", "password": "password123"}
```
3. `POST /api/v1/auth/login` — получите токен (form-urlencoded, не JSON):

```
username=demo@example.com&password=password123
```
4. Нажмите **Authorize** (вверху справа), вставьте `access_token`
5. `GET /api/v1/products` — увидите 3 продукта
6. `POST /api/v1/applications` — создайте заявку
7. `POST /api/v1/applications/{id}/submit` — отправьте
8. `GET /api/v1/applications/{id}/history` — история

### 6.2. Через curl.exe (Windows)

PowerShell с curl.exe плохо работает с JSON — используйте `-d @file.json`:

```
'{"email":"demo@example.com","password":"password123"}' | Out-File body.json -Encoding utf8
curl.exe -X POST http://127.0.0.1:8000/api/v1/auth/register -H "Content-Type: application/json" -d "@body.json"
```

## 7. Переменные окружения

| Переменная ↕▾ | Назначение ↕▾ | Пример ↕▾ |
|---|---|---|
| −`DATABASE_URL` | Подключение к БД | `postgresql+psycopg://smart_credit:pass@localhost:5432/smart_credit` |
| −`JWT_SECRET_KEY` | Подпись JWT (≥32 символа) | `secrets.token_urlsafe(48)` |
| −`JWT_ALGORITHM` | Алгоритм | `HS256` |
| −`ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни токена | `60` |
| −`CORS_ORIGINS` | Разрешённые origin | `http://localhost:5173` |
| −`API_V1_PREFIX` | Префикс API | `/api/v1` |
| −`APP_ENV` | Режим | `local` / `docker` |
⚙

## 8. Устранение проблем

### `docker: The term 'docker' is not recognized`

Docker Desktop не установлен или не в PATH. Установите: https://www.docker.com/products/docker-desktop/

### `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`

Docker Desktop не запущен. Запустите, дождитесь зелёного кита.

### `bind: address already in use` на порту 8000

Остановите локальный uvicorn или другой процесс на 8000:

```
Get-NetTCPConnection -LocalPort 8000
```

### `bind: address already in use` на порту 5433

У вас уже есть Postgres на 5433. Поменяйте в `docker-compose.yml` `"5433:5432"` на `"5434:5432"`.

### `alembic: The term 'alembic' is not recognized`

Не активирован `.venv`. Используйте:

```
.\.venv\Scripts\python.exe -m alembic upgrade head
```

### `pytest: The term 'pytest' is not recognized`

То же. Используйте:

```
.\.venv\Scripts\python.exe -m pytest -v
```

### `ModuleNotFoundError: No module named 'app'`

Запускаете скрипт из неправильной папки. Все команды — из `backend/`, кроме `docker compose` (из корня).

### `ModuleNotFoundError: No module named 'psycopg'`

Не установлены зависимости. Выполните:

```
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### `InsecureKeyLengthWarning: The HMAC key is ...`

`JWT_SECRET_KEY` короче 32 байт. Сгенерируйте новый:

```
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

И вставьте в `backend/.env`.

## 9. Структура проекта

```
smart-credit-cabinet/
├── backend/
│   ├── app/               # FastAPI-приложение
│   │   ├── api/           # эндпоинты
│   │   ├── core/          # config, database, security, json_type
│   │   ├── models/        # SQLAlchemy-модели (7 таблиц)
│   │   ├── schemas/       # Pydantic
│   │   ├── services/      # бизнес-логика
│   │   └── main.py
│   ├── alembic/           # 12 миграций
│   ├── scripts/           # seed_products.py
│   ├── tests/             # 84 теста
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/              # React + TypeScript (в разработке)
├── docs/                  # архитектура, API, модель данных
├── docker-compose.yml
├── .env.example
├── README.md              # обзор проекта
└── README-setup.md        # эта инструкция
```

## 10. Документация

- README.md — обзор проекта
- [docs/architecture.md](https://docs/architecture.md) — архитектура
- [docs/data-model.md](https://docs/data-model.md) — 7 таблиц, миграции
- [docs/application-states.md](https://docs/application-states.md) — статусы заявки
- [docs/api.md](https://docs/api.md) — все эндпоинты
- [docs/openapi.json](https://docs/openapi.json) — OpenAPI-спецификация
- [docs/api-requests.http](https://docs/api-requests.http) — примеры запросов
- [docs/test-scenarios.md](https://docs/test-scenarios.md) — тестовые сценарии

## 11. Проверка «с чистого листа»

Быстрый чек, что всё воспроизводится:

```
git clone https://github.com/lllyll45/smart-credit-cabinet.git fresh-test
cd fresh-test
docker compose up --build
```

В другом окне:

```
curl.exe http://127.0.0.1:8000/health
curl.exe http://127.0.0.1:8000/api/v1/products
```

Если оба вернули данные — окружение воспроизводится корректно.

