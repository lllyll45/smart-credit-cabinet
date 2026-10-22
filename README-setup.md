# Smart Credit Cabinet

Веб-приложение для подбора кредитных продуктов для бизнеса и управления кредитными заявками.

## Технологии

- **Backend:** Python, FastAPI
- **База данных:** PostgreSQL
- **ORM:** SQLAlchemy
- **Миграции БД:** Alembic
- **API-документация:** Swagger / OpenAPI
- **Конфигурация:** переменные окружения (`.env`)

## Структура проекта

```text
smart-credit-cabinet/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── docs/
│   └── api-contract.md
├── .gitignore
└── README.md
```

Структура отражает основные каталоги проекта. По мере разработки в них будут добавляться новые файлы.

## 1. Требования

Перед началом работы установите:

- Git
- Python 3.13
- PostgreSQL 18
- Редактор кода, например Visual Studio Code или PyCharm

Для проверки установки выполните в PowerShell:

```powershell
git --version
python --version
psql --version
```

## 2. Клонирование репозитория

Скопируйте URL репозитория из GitHub и выполните:

```powershell
git clone <URL_РЕПОЗИТОРИЯ>
cd smart-credit-cabinet
```

Вместо `<URL_РЕПОЗИТОРИЯ>` укажите настоящий адрес репозитория команды.

## 3. Настройка PostgreSQL

Убедитесь, что служба PostgreSQL запущена.

Откройте SQL Shell (`psql`) и подключитесь к серверу под пользователем `postgres`.

Создайте отдельного пользователя и базу данных для проекта:

```sql
CREATE USER smart_credit WITH PASSWORD 'YOUR_LOCAL_PASSWORD';
CREATE DATABASE smart_credit OWNER smart_credit;
```

Замените `YOUR_LOCAL_PASSWORD` на собственный пароль. Если пользователь или база уже существуют, повторно создавать их не нужно.

## 4. Настройка backend

Перейдите в папку backend:

```powershell
cd backend
```

Создайте виртуальное окружение:

```powershell
python -m venv .venv
```

Активируйте его:

```powershell
.\.venv\Scripts\Activate.ps1
```

Если PowerShell запрещает запуск скрипта активации, можно использовать интерпретатор напрямую:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Установите зависимости:

```powershell
python -m pip install -r requirements.txt
```

## 5. Настройка переменных окружения

Создайте локальный файл `.env` в папке `backend`, скопировав шаблон `.env.example`, если он находится в этой папке.

Если шаблон хранится в корне репозитория, находясь в `backend`, выполните:

```powershell
Copy-Item ..\.env.example .\.env
```

Откройте `backend/.env` и настройте параметры:

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

Замените `YOUR_LOCAL_PASSWORD` на пароль созданного пользователя PostgreSQL.

Сгенерировать случайный секрет для локальной конфигурации можно командой:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Скопируйте результат в `JWT_SECRET_KEY`.

**Важно:** файл `.env` содержит локальные настройки и секреты. Не загружайте его в GitHub и не отправляйте другим участникам. Каждый участник создаёт собственный `.env`.

## 6. Запуск backend

Находясь в папке `backend` и используя активированное виртуальное окружение, выполните:

```powershell
python -m uvicorn app.main:app --reload
```

Если запуск прошёл успешно, приложение будет доступно по адресу:

http://127.0.0.1:8000

Документация API в Swagger:

http://127.0.0.1:8000/docs

Альтернативный формат OpenAPI:

http://127.0.0.1:8000/openapi.json

Чтобы остановить сервер, нажмите `Ctrl+C` в терминале.

## 7. Проверка подключения к PostgreSQL

Откройте второй терминал PowerShell, перейдите в `backend` и активируйте виртуальное окружение.

Выполните:

```powershell
@'
from sqlalchemy import text
from app.core.database import engine

with engine.connect() as connection:
    print("Результат:", connection.execute(text("SELECT 1")).scalar())
'@ | python -
```

Если команда выводит `Результат: 1`, подключение к базе данных работает.

## 8. Работа с базой данных и миграциями

Для работы с базой данных используется SQLAlchemy. Общий базовый класс моделей находится в `app.core.database`.

Для управления изменениями структуры БД используется Alembic.

Перед выполнением миграций убедитесь, что конфигурация Alembic и файлы миграций уже настроены в проекте. Если они настроены, миграции применяются командой:

```powershell
alembic upgrade head
```

Новые миграции создаются командой:

```powershell
alembic revision --autogenerate -m "migration description"
```

Перед применением сгенерированной миграции проверьте её содержимое.

## 9. Работа с Git

Перед началом работы получите последние изменения:

```powershell
git pull
```

После внесения изменений проверьте статус:

```powershell
git status
```

Добавьте нужные файлы и создайте коммит:

```powershell
git add .
git commit -m "Describe your changes"
```

Отправьте изменения в свою ветку:

```powershell
git push
```

Рекомендуется работать в отдельных ветках и создавать Pull Request перед объединением изменений в основную ветку.

## 10. Важные правила

- Не коммитьте `.env`, пароли, токены и другие секреты.
- Не добавляйте в Git виртуальное окружение `.venv`, кэш Python и `node_modules`.
- Обновляйте `requirements.txt`, когда добавляете новые Python-зависимости.
- Используйте общий контракт API из `docs/api-contract.md` при реализации эндпоинтов.
- Для доступа к БД в обработчиках FastAPI используйте `Depends(get_db)`.
- Для SQLAlchemy-моделей используйте общий `Base`.
- Для изменения структуры базы данных используйте Alembic.
- Перед отправкой изменений проверяйте `git status` и запускайте доступные тесты.

## Устранение распространённых проблем

**Ошибка авторизации PostgreSQL**

Проверьте имя пользователя, пароль, имя базы и порт в `DATABASE_URL`.

**Ошибка подключения к `localhost:5432`**

Убедитесь, что PostgreSQL запущен и слушает порт `5432`.

**Ошибка `ModuleNotFoundError`**

Активируйте виртуальное окружение и установите зависимости из `requirements.txt`.

**Swagger не открывается**

Проверьте, что Uvicorn запущен без ошибок, и откройте http://127.0.0.1:8000/docs.

**Таблицы отсутствуют**

Проверьте наличие и настройку миграций Alembic. Создание базы PostgreSQL само по себе не создаёт таблицы приложения.

---

Документ описывает локальную настройку backend. Инструкции по запуску frontend и Docker Compose будут добавлены после включения соответствующих компонентов в общий процесс разработки.
