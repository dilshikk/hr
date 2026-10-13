# Архитектура

```
Telegram-бот (bot/)  -->  кнопка Mini App
Mini App (frontend/) --\
Админ-панель         ---+--> REST API /api/v1 (backend/app) --> PostgreSQL
(admin-panel/)       --/
```

## Слои бэкенда (backend/app)
- `api/v1` — тонкие маршруты: разбор запроса, проверка прав, вызов сервиса.
- `services` — бизнес-логика (воронка, вход, права на данные). Ошибки — `ServiceError`.
- `repositories` — единственное место, где пишутся запросы к БД.
- `models` — таблицы SQLAlchemy; `schemas` — форматы запросов и ответов.
- `core` — настройки, безопасность, роли, логи, подключение к БД.
- `integrations`, `tasks` — заготовки (Telegram, Google Sheets, AI, фоновые задачи).

Фронтенд и бот не обращаются к базе напрямую. Бот и API используют общие настройки из `backend/app/core/config.py`.

## Миграции
Alembic: `alembic upgrade head`. Первая миграция — `migrations/versions/0001_initial.py`.
