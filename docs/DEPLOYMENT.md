# Развёртывание на VPS

1. Пользователь и каталог: `useradd -r madohr`, код в `/opt/mado_hr`.
2. Окружение: `python3 -m venv .venv && .venv/bin/pip install -e .`
3. Секреты: `/etc/mado-hr/mado-hr.env` (по образцу `.env.example`), права `600`, владелец `madohr`.
4. PostgreSQL: создать БД и пользователя, указать `DATABASE_URL=postgresql+asyncpg://...`.
5. Миграции: `.venv/bin/alembic upgrade head`.
6. systemd: скопировать `deploy/systemd/*.service` в `/etc/systemd/system/`, затем `systemctl enable --now mado-hr-api mado-hr-bot`.
7. nginx: проксировать `https://<домен>/api/` на `127.0.0.1:8000`, раздавать собранный Mini App. HTTPS обязателен (Telegram WebApp требует https).
8. `ALLOWED_ORIGINS` = домен Mini App, `WEBAPP_URL` = https-адрес Mini App.

## Бэкапы
Ежедневный `pg_dump` в `deploy/backup/` (скрипт ещё не написан). Дампы не коммитить — они в `.gitignore`.
