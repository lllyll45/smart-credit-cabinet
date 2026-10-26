# Smart Credit Cabinet

**«Умный кредитный кабинет»** — проект для хакатона Альфа-Банка. Это MVP веб-сервиса, который помогает предпринимателям малого бизнеса изучать кредитные предложения, оценивать условия, получать рекомендации и подавать заявки. Сотрудник банка может просматривать заявки и отмечать результат их рассмотрения.

> Проект демонстрационный: каталог содержит тестовые кредитные продукты, предварительные расчёты и оценки не являются предложением или решением банка. Реальные банковские интеграции, передача заявки в банк и выдача кредита не реализованы.

## Возможности

- Регистрация, вход и аутентификация по JWT.
- Каталог активных кредитных продуктов.
- Расчёт аннуитетного платежа и сравнение продуктов по общей выплате.
- Профиль бизнеса предпринимателя.
- Подбор продуктов с оценкой соответствия и поясняющими причинами.
- Создание и отправка кредитной заявки, просмотр её статуса и истории.
- Интерфейс сотрудника для проверки, запроса дополнительной информации, предложения альтернативы, одобрения или отклонения заявки.

Заявка требует заполненного профиля бизнеса с месячной выручкой. При отправке backend рассчитывает платежи и предварительно оценивает долговую нагрузку: эта оценка не является автоматическим банковским одобрением. Текущий API не поддерживает ответ пользователя на запрос дополнительной информации или альтернативное предложение.

## Технологии

| Область | Технологии |
|---|---|
| Frontend | React 19, TypeScript, Vite, React Router, Axios |
| Backend | Python, FastAPI, Pydantic |
| База данных | PostgreSQL, SQLAlchemy |
| Миграции | Alembic |
| Безопасность | JWT, Argon2 |
| Автотесты | pytest, SQLite in-memory |
| Контейнеризация | Docker, Docker Compose |

## Структура проекта

```text
backend/
  app/
    api/          HTTP API
    core/         настройки, база данных, безопасность
    models/       SQLAlchemy-модели
    schemas/      схемы запросов и ответов
    services/     бизнес-логика
  alembic/        миграции базы данных
  scripts/        вспомогательные скрипты, в том числе демо-данные
  tests/          автоматические тесты
frontend/
  src/
    app/          приложение и маршрутизация
    features/     функции и API-клиенты по областям
    pages/        страницы приложения
docs/             документация API и архитектуры
```

## Быстрый запуск с Docker Compose

Необходимы Git и Docker Desktop с поддержкой `docker compose`. Команды ниже рассчитаны на PowerShell из корня репозитория.

1. Используйте коммитимый [шаблон `.env.example`](.env.example), чтобы создать локальный файл настроек для Docker Compose:

   ```powershell
   Copy-Item .env.example .env
   ```

2. В созданном локальном `.env` замените значения-заглушки `POSTGRES_PASSWORD` и `JWT_SECRET_KEY` на собственные. Не коммитьте `.env`: он игнорируется Git. Сгенерировать JWT-секрет можно, например, командой:

   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

3. Соберите и запустите PostgreSQL, backend и frontend:

   ```powershell
   docker compose up --build -d
   ```

4. При старте backend-контейнер автоматически применяет миграции Alembic и запускает синтетическое наполнение из `backend/app/seed.py` перед запуском API. Seed идемпотентен и повторно запускается при перезапуске контейнера. Проверить ход запуска можно командой:

   ```powershell
   docker compose logs -f backend
   ```

   Seed создаёт демонстрационные аккаунты и продукты, бизнес-профили и заявки. Для всех демо-аккаунтов пароль `DemoPass123!`; используйте эти учётные данные только в локальной демонстрационной среде, не публикуйте сервис как production.

   API будет доступно только если миграции и seed завершились без ошибки. Проверьте состояние контейнеров командой `docker compose ps`. Если в логах backend есть `password authentication failed`, пароль в текущем `.env` не совпадает с паролем PostgreSQL, сохранённым при первоначальном создании Docker volume. Изменение `POSTGRES_PASSWORD` в `.env.example` или `.env` само по себе не меняет пароль в уже инициализированной базе: укажите прежний пароль или согласованно обновите пароль пользователя PostgreSQL. Не удаляйте volume, если нужно сохранить данные.

5. Откройте приложение и API после успешного запуска backend:

   - Frontend: <http://localhost:5173>
   - API: <http://localhost:8000>
   - Swagger UI: <http://localhost:8000/docs>
   - Проверка API: <http://localhost:8000/health>

Остановить сервисы, сохранив данные PostgreSQL:

```powershell
docker compose down
```

Чтобы также удалить данные базы из Docker volume:

```powershell
docker compose down -v
```

## Локальный запуск без Docker

Нужны Python (Docker-образ backend использует Python 3.12), Node.js 22 или совместимая версия, npm и PostgreSQL. PostgreSQL можно запустить локально; остальные шаги ниже выполняются в отдельных терминалах из корня репозитория.

### 1. Подготовьте PostgreSQL

Создайте базу данных и пользователя (пример для `psql`, выполненный администратором PostgreSQL):

```sql
CREATE USER smart_credit WITH PASSWORD 'replace_with_a_local_password';
CREATE DATABASE smart_credit OWNER smart_credit;
```

Пользуйтесь собственным паролем. Не сохраняйте реальные пароли в репозитории.

### 2. Настройте и запустите backend

Создайте виртуальное окружение, установите зависимости и скопируйте коммитимый шаблон [`.env.example`](.env.example) в локальный `backend/.env`:

```powershell
Set-Location backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item ..\.env.example .env
```

Отредактируйте локальный `backend/.env`: укажите пароль созданного пользователя PostgreSQL в `DATABASE_URL` и замените шаблонное значение `JWT_SECRET_KEY` собственным секретом. `backend/.env` — локальная конфигурация и не должна коммититься. Например:

```dotenv
DATABASE_URL=postgresql+psycopg://smart_credit:replace_with_a_local_password@localhost:5432/smart_credit
JWT_SECRET_KEY=replace_with_a_long_random_secret
```

Затем выполните миграции, загрузите синтетические данные и запустите API:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m app.seed
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Backend будет доступен по адресу <http://127.0.0.1:8000>. Для остановки нажмите `Ctrl+C`.

### 3. Запустите frontend

В новом терминале, из корня репозитория:

```powershell
Set-Location frontend
npm ci
npm run dev
```

Откройте <http://localhost:5173>. По умолчанию frontend обращается к backend по `http://127.0.0.1:8000/api/v1`. Для другого адреса API задайте `VITE_API_BASE_URL` при запуске Vite.

## Тесты

Backend-тесты используют SQLite in-memory, поэтому отдельная тестовая БД PostgreSQL не нужна. Из каталога `backend`:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

При последней проверке все 84 теста прошли. В выводе pytest может отображаться предупреждение Starlette о совместимости TestClient и `httpx`.

Проверки frontend:

```powershell
Set-Location frontend
npm run lint
npm run build
```

## API

Корневой префикс API — `/api/v1`. Основные группы:

| Возможность | Маршруты |
|---|---|
| Авторизация | `/auth/register`, `/auth/login`, `/auth/me` |
| Кредитные продукты | `/products`, `/products/{product_id}` |
| Калькулятор | `/calculator/calculate`, `/calculator/compare` |
| Профиль бизнеса | `/business-profile` |
| Заявки и история | `/applications`, `/applications/{application_id}`, `/applications/{application_id}/history` |
| Операции сотрудника | `/applications/staff`, `/applications/{application_id}/check`, `/request-info`, `/offer-alternative`, `/approve`, `/reject` |
| Рекомендации | `/recommendations`, `/recommendations/{recommendation_id}` |

Интерактивная документация доступна по `/docs` после запуска backend. Для подробных контрактов и примеров см. [API-документацию](docs/api.md).

## Документация

- [Архитектура](docs/architecture.md)
- [Модель данных](docs/data-model.md)
- [Статусы заявок](docs/application-states.md)
- [API](docs/api.md)
- [Сценарии тестирования](docs/test-scenarios.md)
- [Подробная инструкция по запуску](README-setup.md)
