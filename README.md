# MADO HR Platform

Telegram HR-бот → полноценная HR-платформа: Telegram Bot, Telegram Mini App, Backend API, админ-панель, PostgreSQL, 2FA.

Текущий бот: https://github.com/dilshikk/mado_jbot

## Документация
- [Техническое задание](docs/TZ.md)
- [План реализации](docs/ROADMAP.md)
- [Перенос на VPS](docs/VPS_RUNBOOK.md)

## Структура
| Каталог | Назначение |
|---|---|
| bot/ | Telegram handlers, keyboards, middleware |
| api/ | FastAPI routers, dependencies, schemas |
| domain/ | бизнес-правила HR и pipeline |
| db/ | модели SQLAlchemy, сессии, репозитории |
| services/ | уведомления, Google Sheets, AI, файлы |
| security/ | initData, 2FA, RBAC, сессии |
| frontend/ | React + TypeScript Mini App |
| alembic/ | миграции |
| tests/ | unit, integration, security |
| deploy/ | systemd, nginx, backup/restore |

## Статус
Этап 0: аудит. Перечисленные в ТЗ функции — требования к разработке, а не реализованный функционал.
