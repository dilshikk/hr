# Архитектура

## Компоненты
- **Telegram-бот** (`bot/`, aiogram 3) — точка входа: /start открывает Mini App; позже — уведомления и команды администратора.
- **Backend API** (`backend/app/`, FastAPI) — вся бизнес-логика и проверка прав.
- **Mini App** (`frontend/`) и **админ-панель** (`admin-panel/`) — клиенты API. Пока не созданы.
- **БД** — PostgreSQL в продакшене, SQLite локально. SQLAlchemy 2 (async), миграции Alembic.

## Слои backend
| Слой | Папка | Ответственность |
|---|---|---|
| API | `api/v1/` | HTTP-маршруты, валидация, вызов сервисов |
| Зависимости | `api/deps.py` | текущий пользователь из сессии, проверка прав |
| Ядро | `core/` | настройки, БД, безопасность, роли, логи |
| Модели | `models/` | таблицы: `org` (филиалы, пользователи), `recruiting` (вакансии, кандидаты, история), `system` (сессии, аудит) |
| Схемы | `schemas/` | форматы запросов и ответов |
| Сервисы | `services/` | бизнес-правила (воронка найма) |
| Репозитории | `repositories/` | запросы к БД (выносить по мере роста) |
| Интеграции | `integrations/` | Telegram, Google Sheets, AI (заготовки) |
| Задачи | `tasks/` | фоновые задачи |

https://github.com/dilshikk/hr/
│
├── bot/                         # Telegram-бот
│   ├── main.py                  # Запуск бота
│   ├── handlers/
│   │   ├── start.py             # /start и открытие Mini App
│   │   ├── notifications.py     # Уведомления
│   │   └── admin.py             # Команды администратора
│   ├── keyboards/
│   │   └── main_menu.py
│   ├── middlewares/
│   └── services/
│
├── backend/                     # Серверное API
│   └── app/
│       ├── main.py              # Запуск FastAPI
│       ├── api/
│       │   └── v1/
│       │       ├── auth.py
│       │       ├── candidates.py
│       │       ├── vacancies.py
│       │       ├── interviews.py
│       │       ├── employees.py
│       │       ├── branches.py
│       │       ├── admin.py
│       │       └── reports.py
│       ├── core/
│       │   ├── config.py        # Настройки
│       │   ├── security.py      # Авторизация и безопасность
│       │   ├── permissions.py   # Роли и права
│       │   └── logging.py
│       ├── models/              # Модели БД
│       ├── schemas/             # Форматы запросов и ответов
│       ├── repositories/        # Работа с данными
│       ├── services/            # Бизнес-логика
│       ├── integrations/
│       │   ├── telegram.py
│       │   ├── google_sheets.py
│       │   └── ai.py
│       └── tasks/               # Фоновые задачи
│
├── frontend/                    # Telegram Mini App
│   ├── src/
│   │   ├── app/
│   │   ├── pages/
│   │   │   ├── Home/
│   │   │   ├── Vacancies/
│   │   │   ├── Application/
│   │   │   ├── MyApplication/
│   │   │   └── Interviews/
│   │   ├── components/
│   │   ├── features/
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── hooks/
│   │   ├── types/
│   │   └── locales/             # RU
│   ├── package.json
│   └── vite.config.ts
│
├── admin-panel/                 # Веб-панель HR и руководства
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── modules/
│   │   └── services/
│   └── package.json
│
├── migrations/                  # Миграции БД
├── tests/
│   ├── test_auth.py
│   ├── test_permissions.py
│   ├── test_candidates.py
│   └── test_applications.py
│
├── deploy/
│   ├── nginx/
│   ├── systemd/
│   ├── scripts/
│   └── backup/
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── SECURITY.md
│
├── .env.example
├── .gitignore
├── alembic.ini
├── pyproject.toml
├── README.md
└── docker-compose.yml            # Если выбран Docker
## Воронка найма
`new → review → contact → interview → (trial) → offer → hired`. С любого незавершённого этапа — `rejected` (с причиной) или `reserve`. Из `reserve` можно вернуться в `review`/`contact`. `hired` и `rejected` — конечные. Каждый переход пишется в `pipeline_events`.

## Импорты
Пакет backend — `app` (корень `backend/`). Бот импортирует настройки из `app.core.config`, поэтому запускается с `PYTHONPATH=.:backend`.
