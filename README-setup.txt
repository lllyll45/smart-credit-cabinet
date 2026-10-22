Smart Credit Cabinet — подключение контрактов и базовой конфигурации

1. Скопируйте .env.example в .env в корне репозитория и замените секреты.
2. Проверьте, что .env добавлен в .gitignore.
3. Перенесите зависимости из backend/requirements-config.txt в backend/requirements.txt
   или в pyproject.toml — в зависимости от текущего способа управления зависимостями.
4. Убедитесь, что существует backend/app/core/__init__.py (может быть пустым).
5. Если config.py или database.py уже есть, объедините изменения, не затирая код вслепую.
6. Для FastAPI используйте settings из app.core.config и Depends(get_db) там, где нужна БД.
7. Используйте Base из app.core.database для SQLAlchemy-моделей.
8. Для схем БД используйте Alembic; не полагайтесь на create_all() как на миграции.
9. При запуске backend внутри Docker Compose в DATABASE_URL укажите имя сервиса БД (например, db),
   а не localhost. При запуске uvicorn напрямую используйте localhost.
10. Swagger/OpenAPI доступен по /docs после запуска приложения.

Примечание: JWT_SECRET_KEY в примере — только заглушка. Перед использованием JWT замените её.
