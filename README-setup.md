# Smart Credit Cabinet

Веб-приложение для подбора кредитных продуктов для бизнеса и управления кредитными заявками.

Этот документ описывает настройку и запуск backend на Windows для локальной разработки.

## Технологии

- **Язык:** Python 3.13
- **Backend:** FastAPI
- **База данных:** PostgreSQL 18
- **ORM:** SQLAlchemy
- **Миграции БД:** Alembic
- **Авторизация:** JWT
- **Хеширование паролей:** Argon2
- **Документация API:** Swagger / OpenAPI
- **Конфигурация:** переменные окружения (`.env`)

## Структура проекта

```text
smart-credit-cabinet/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   └── applications.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── alembic/
│   │   └── versions/
│   ├── tests/
│   ├── .env.example
│   ├── alembic.ini
│   └── requirements.txt
├── docs/
├── .gitignore
└── README.md
```

Структура показывает основные каталоги и ожидаемые файлы backend. Наличие конкретных файлов следует сверять с текущей версией репозитория.

## 1. Требования

Перед началом работы установите:

- Git
- Python 3.13
- PostgreSQL 18
- Редактор кода, например Visual Studio Code, PyCharm или IntelliJ IDEA

Проверьте установку в PowerShell:

```powershell
git --version
python --version
psql --version
```

Если команда `python` не распознаётся, проверьте установку Python и его добавление в `PATH`.

## 2. Клонирование репозитория

Скопируйте URL репозитория команды из GitHub и выполните:

```powershell
git clone <URL_РЕПОЗИТОРИЯ>
cd smart-credit-cabinet
```

Замените `<URL_РЕПОЗИТОРИЯ>` на реальный адрес репозитория.

Получите последние изменения:

```powershell
git pull
```

## 3. Настройка PostgreSQL

Убедитесь, что служба PostgreSQL запущена.

Откройте SQL Shell (`psql`) и подключитесь к серверу под пользователем `postgres`.

Создайте отдельного пользователя и базу данных проекта:

```sql
CREATE USER smart_credit WITH PASSWORD 'YOUR_LOCAL_PASSWORD';
CREATE DATABASE smart_credit OWNER smart_credit;
```

Замените `YOUR_LOCAL_PASSWORD` на собственный пароль.

Если пользователь или база уже существуют, повторно создавать их не нужно. Используйте существующие настройки подключения.

## 4. Настройка виртуального окружения

Перейдите в каталог backend:

```powershell
cd backend
```

Создайте виртуальное окружение:

```powershell
python -m venv .venv
```

Установите зависимости проекта:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

При желании активируйте виртуальное окружение:

```powershell
.\.venv\Scripts\Activate.ps1
```

Если PowerShell запрещает запуск скрипта активации, продолжайте использовать `.\.venv\Scripts\python.exe` в командах — активация не обязательна.

## 5. Настройка переменных окружения

В каталоге `backend` создайте локальный файл `.env` на основе `backend/.env.example`.

Находясь в каталоге `backend`, выполните:

```powershell
Copy-Item .env.example .env
```

Если файл `.env` уже существует, не перезаписывайте его без необходимости.

Откройте `backend/.env` и настройте параметры. Пример:

```dotenv
APP_NAME=Smart Credit Cabinet
APP_ENV=local
DEBUG=true
API_V1_PREFIX=/api/v1

DATABASE_URL=postgresql+psycopg://smart_credit:YOUR_LOCAL_PASSWORD@localhost:5432/smart_credit

JWT_SECRET_KEY=REPLACE_WITH_A_RANDOM_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Замените `YOUR_LOCAL_PASSWORD` на пароль пользователя PostgreSQL.

Сгенерируйте случайный секрет для JWT:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

Скопируйте результат в `JWT_SECRET_KEY`. Не используйте приведённое примерное значение в качестве настоящего секрета.

**Важно:**

- Не загружайте `.env` в GitHub.
- Не отправляйте пароли и JWT-секреты в общие чаты.
- Каждый участник команды создаёт собственный `.env`.
- В `.env.example` храните только примерные значения без настоящих секретов.

## 6. Применение миграций базы данных

Все команды этого раздела выполняются из каталога `backend`.

Проверьте текущую версию схемы:

```powershell
.\.venv\Scripts\python.exe -m alembic current
```

Примените все существующие миграции:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Команда создаст или обновит таблицы согласно существующим миграциям.

В проекте предусмотрены миграции для таблицы пользователей и таблицы кредитных заявок. В частности, миграция `d2eefc340c25` создаёт таблицу `credit_applications`.

Не создавайте таблицы вручную, если они уже управляются Alembic.

### Создание новой миграции

После изменения SQLAlchemy-моделей создайте миграцию:

```powershell
.\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "describe changes"
```

Перед применением обязательно проверьте сгенерированный файл в `alembic/versions/`.

Затем примените миграцию:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Автоматическая генерация миграций не заменяет ручную проверку изменений.

## 7. Проверка подключения к PostgreSQL

Убедитесь, что вы находитесь в каталоге `backend`.

Выполните:

```powershell
@'
from sqlalchemy import text
from app.core.database import engine

with engine.connect() as connection:
    print("Результат:", connection.execute(text("SELECT 1")).scalar())
'@ | .\.venv\Scripts\python.exe -
```

Если вывод содержит:

```text
Результат: 1
```

подключение к PostgreSQL работает.

## 8. Запуск backend

Находясь в каталоге `backend`, выполните:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

После успешного запуска сервер будет доступен по адресу:

- Приложение: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

Для остановки сервера нажмите `Ctrl+C`.

## 9. Проверка API

Откройте Swagger:

http://127.0.0.1:8000/docs

В документации доступны эндпоинты авторизации и работы с кредитными заявками.

### Авторизация

- `POST /api/v1/auth/register` — регистрация пользователя.
- `POST /api/v1/auth/login` — вход и получение токена.
- `GET /api/v1/auth/me` — получение данных текущего пользователя.

### Кредитные заявки

- `POST /api/v1/applications` — создание заявки.
- `GET /api/v1/applications` — получение списка заявок текущего пользователя.
- `GET /api/v1/applications/{application_id}` — получение заявки по идентификатору.
- `PATCH /api/v1/applications/{application_id}` — редактирование заявки.
- `POST /api/v1/applications/{application_id}/submit` — отправка заявки.

Для проверки защищённых эндпоинтов сначала авторизуйтесь через кнопку **Authorize** в Swagger.

Основные операции с кредитными заявками уже проверялись вручную и возвращали успешные HTTP-ответы.

## 10. Работа с Git

Перед началом работы получите актуальные изменения:

```powershell
git switch main
git pull
```

Создайте отдельную ветку для задачи:

```powershell
git switch -c feature/task-name
```

После внесения изменений проверьте состояние репозитория:

```powershell
git status
```

Добавьте необходимые файлы и создайте коммит:

```powershell
git add .
git commit -m "Describe your changes"
```

Отправьте ветку в удалённый репозиторий:

```powershell
git push -u origin feature/task-name
```

Затем создайте Pull Request в GitHub и дождитесь проверки перед объединением с основной веткой.

Если основная ветка в репозитории называется не `main`, используйте фактическое название ветки команды.

## 11. Важные правила разработки

- Не коммитьте `.env`, пароли, токены и другие секреты.
- Не добавляйте в Git `.venv`, `__pycache__`, файлы `.pyc` и другие временные файлы.
- Обновляйте `requirements.txt` при изменении зависимостей.
- Используйте общий контракт API из `docs/api-contract.md`, если он присутствует в репозитории.
- Для доступа к базе данных в обработчиках FastAPI используйте `Depends(get_db)`.
- Для SQLAlchemy-моделей используйте общий `Base`.
- Для изменения структуры базы данных используйте Alembic.
- Перед отправкой изменений проверяйте `git status` и запускайте доступные тесты.
- Не изменяйте общие модели и API-контракты без согласования с участниками команды.

## 12. Устранение распространённых проблем

### Ошибка подключения к PostgreSQL

Проверьте:

- запущена ли служба PostgreSQL;
- правильны ли имя пользователя и пароль;
- существует ли база `smart_credit`;
- совпадают ли адрес и порт с параметрами в `DATABASE_URL`.

### Ошибка `ModuleNotFoundError`

Установите зависимости из каталога `backend`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Ошибка `relation does not exist`

Таблица отсутствует в подключённой базе данных. Проверьте `DATABASE_URL` и примените миграции:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

### Ошибка авторизации

Проверьте, что запрос содержит действительный JWT-токен. В Swagger используйте кнопку **Authorize**.

### Ошибка `alembic` или отсутствует конфигурация

Убедитесь, что в `backend` существуют `alembic.ini` и каталог `alembic/`, а зависимости установлены в `.venv`.

### Swagger не открывается

Убедитесь, что Uvicorn запущен без ошибок, и откройте:

http://127.0.0.1:8000/docs

## 13. Текущее состояние проекта

На данный момент реализованы:

- настройка backend на FastAPI;
- подключение PostgreSQL через SQLAlchemy;
- модели пользователей и кредитных заявок;
- JWT-авторизация;
- миграции Alembic;
- основные API-операции с кредитными заявками.

Каталог кредитных продуктов, алгоритм подбора предложений и пользовательский интерфейс относятся к следующим этапам разработки.

---

README описывает локальную настройку backend. Инструкции по запуску frontend и Docker Compose будут добавлены после настройки и проверки соответствующих компонентов.