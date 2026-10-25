# Архитектура системы «Умный кредитный кабинет предпринимателя»

## 1. Назначение системы

«Умный кредитный кабинет предпринимателя» — веб-приложение для подбора кредитных предложений и подачи заявок на кредитование малого бизнеса.

Система позволяет пользователю зарегистрироваться, заполнить профиль бизнеса, подобрать подходящие кредитные продукты, оформить и отправить заявку, а сотруднику банка — рассмотреть её и принять решение.

Проект реализуется в формате MVP для демонстрации полного цикла. Реальные банковские и государственные интеграции не используются.

## 2. Технологический стек

| Компонент | Технология | Назначение |
|---|---|---|
| Frontend | React, TypeScript, Vite | Пользовательский интерфейс |
| Backend | Python 3.13, FastAPI | REST API и бизнес-логика |
| Валидация | Pydantic | Схемы запросов и ответов |
| БД | PostgreSQL | Хранение данных |
| ORM | SQLAlchemy | Работа с данными |
| Миграции | Alembic | Управление схемой БД |
| Аутентификация | JWT, Argon2 | Авторизация и хеширование паролей |
| Тесты | pytest | 84 теста |
| Документация API | OpenAPI, Swagger UI | `/docs` |
| Запуск | Docker, Docker Compose | Воспроизводимый запуск |

## 3. Общая архитектура

Три основных компонента:
1. **Frontend** — интерфейс, отправляет HTTP-запросы к backend.
2. **Backend** — REST API, бизнес-логика, работа с БД.
3. **PostgreSQL** — данные пользователей, заявок, продуктов, истории, профилей, рекомендаций.

Внешние банковские интеграции отсутствуют. Решение по заявке — демонстрационное.

## 4. Структура backend (актуальная)

```text
backend/
├── app/
│   ├── api/
│   │   ├── auth.py              # регистрация, вход, /me
│   │   ├── applications.py      # CRUD, submit, staff-переходы статусов
│   │   ├── products.py          # каталог
│   │   ├── calculator.py        # расчёт и сравнение
│   │   ├── business_profile.py  # GET/PUT профиля бизнеса
│   │   └── recommendations.py   # подбор предложений
│   ├── core/
│   │   ├── config.py            # настройки (.env)
│   │   ├── database.py          # engine, Session, Base
│   │   ├── json_type.py         # JSONB для Postgres / JSON для SQLite
│   │   └── security.py          # JWT, хеширование
│   ├── models/
│   │   ├── user.py              # User
│   │   ├── credit_application.py # CreditApplication
│   │   ├── credit_product.py     # CreditProduct
│   │   ├── application_history.py # ApplicationHistory
│   │   ├── business_profile.py   # BusinessProfile
│   │   └── recommendation.py     # Recommendation, RecommendationItem
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── credit_application.py
│   │   ├── credit_product.py
│   │   ├── calculator.py
│   │   ├── application_history.py
│   │   ├── application_decision.py
│   │   ├── business_profile.py
│   │   └── recommendation.py
│   ├── services/
│   │   ├── auth.py               # регистрация, аутентификация
│   │   ├── calculator.py         # аннуитетный расчёт
│   │   ├── application_processing.py # submit + preliminary_result
│   │   ├── application_history.py    # record_status_change
│   │   └── recommendation.py     # build_recommendations + match_score
│   └── main.py                   # FastAPI, CORS, подключение роутеров
├── alembic/
│   └── versions/                 # 12 миграций
├── scripts/
│   └── seed_products.py          # 3 демо-продукта
├── tests/                        # 84 теста
├── Dockerfile
├── .dockerignore
├── alembic.ini
└── requirements.txt