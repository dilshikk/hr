# MADO HR Platform

Telegram HR-бот → HR-платформа: Telegram Bot, Mini App, Backend API, PostgreSQL. 2FA и админ-панель — после MVP.

Текущий бот: https://github.com/dilshikk/mado_jbot

## Документация
- [Техническое задание](docs/TZ.md)
- [Анализ и границы MVP](docs/ANALYSIS.md)
- [План реализации](docs/ROADMAP.md)
- [Перенос на VPS](docs/VPS_RUNBOOK.md)

## Структура
| Каталог | Назначение | Статус |
|---|---|---|
| config.py | настройки из .env | готово |
| bot/ | /start и кнопка «Открыть HR-панель» | каркас |
| api/ | FastAPI: вход, кандидаты, вакансии | каркас |
| domain/ | правила воронки найма | готово + тесты |
| db/ | модели SQLAlchemy, сессия | каркас (миграций Alembic пока нет) |
| security/ | проверка initData, роли и филиалы | готово + тесты |
| tests/ | unit-тесты | начало |
| frontend/, services/, alembic/ | Mini App, интеграции, миграции | пока пусто |
| deploy/ | systemd | частично |

## Запуск (разработка)
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # заполнить BOT_TOKEN, SESSION_SECRET
pytest
uvicorn api.main:app --reload
python -m bot.main
```

## Статус
Работают только правила воронки, проверка initData и роли (с тестами). API, база и бот — каркас, который ещё не запускался против реальной базы. См. docs/ANALYSIS.md.
