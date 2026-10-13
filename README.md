# MADO HR Platform

Telegram HR-бот → полноценная HR-платформа: Telegram Bot, Telegram Mini App, Backend API, админ-панель, PostgreSQL, 2FA.

Текущий бот: https://github.com/dilshikk/mado_jbot

## Документация
- [Архитектура](docs/ARCHITECTURE.md)
- [API](docs/API.md)
- [Развёртывание](docs/DEPLOYMENT.md)
- [Безопасность](docs/SECURITY.md)

## Структура
| Каталог | Назначение |
|---|---|
| bot/ | Telegram-бот: handlers, keyboards, middlewares |
| backend/app/ | FastAPI: api/v1, core, models, schemas, services, integrations, tasks |
| frontend/ | Telegram Mini App (React + TypeScript) |
| admin-panel/ | Веб-панель HR и руководства |
| migrations/ | Миграции Alembic |
| tests/ | Тесты |
| deploy/ | systemd, nginx, скрипты, бэкапы |
| docs/ | Документация |

## Быстрый старт
```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
alembic revision --autogenerate -m "init" && alembic upgrade head
PYTHONPATH=backend uvicorn app.main:app --reload   # API
PYTHONPATH=.:backend python -m bot.main            # бот
pytest
```

## Статус
Этап 0–1. Готовы: вход через Telegram, сессии, роли, изоляция филиалов, воронка кандидатов, вакансии. Остальное — заготовки.
