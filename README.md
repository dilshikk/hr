# MADO HR Platform

Telegram-бот, Mini App, собственный REST API и PostgreSQL. Без сторонних облачных бэкендов.

## Структура
| Папка | Назначение | Статус |
|---|---|---|
| bot/ | Telegram-бот: /start, кнопка Mini App, уведомления, команды админа | каркас |
| backend/app/ | FastAPI: api/v1, core, models, schemas, repositories, services | MVP-каркас |
| frontend/ | Telegram Mini App (React + Vite) | вход, кандидаты, вакансии |
| admin-panel/ | Веб-панель HR и руководства | заготовка |
| migrations/ | Миграции Alembic (0001 — начальная схема) | готово |
| tests/ | unit-тесты: вход, права, воронка | начало |
| deploy/ | nginx, systemd, скрипты, backup | готово |
| docs/ | ТЗ, архитектура, API, развёртывание, безопасность | готово |

## Запуск (разработка)
```
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env          # заполнить BOT_TOKEN, ADMIN_IDS
alembic upgrade head
pytest
uvicorn backend.app.main:app --reload
python -m bot.main
cd frontend && npm install && npm run dev
```

## Документация
- [ТЗ](docs/TZ.md) · [Анализ и MVP](docs/ANALYSIS.md) · [План](docs/ROADMAP.md)
- [Архитектура](docs/ARCHITECTURE.md) · [API](docs/API.md)
- [Развёртывание](docs/DEPLOYMENT.md) · [Безопасность](docs/SECURITY.md)

## Статус
Код не запускался против реальной базы. Не сделано: 2FA, интервью, документы, экспорт, админ-панель, уведомления, интеграции. Подробности — docs/ANALYSIS.md и docs/SECURITY.md.
