# Развёртывание на VPS

См. также docs/VPS_RUNBOOK.md.

1. Установить Python 3.11+, PostgreSQL, nginx. Создать пользователя `madohr`.
2. Клонировать репозиторий в `/opt/mado_jbot`, создать `.venv`, выполнить `pip install -e .`.
3. Создать `/etc/mado-jbot/mado-jbot.env` по образцу `.env.example` (права 600).
4. `alembic upgrade head`.
5. Скопировать `deploy/systemd/*.service` в `/etc/systemd/system/`, включить `mado-api` и `mado-bot`.
6. Собрать Mini App (`cd frontend && npm ci && npm run build`), положить `dist` в `/var/www/mado-hr/miniapp`.
7. Настроить nginx по `deploy/nginx/mado-hr.conf` и HTTPS-сертификат.
8. Бэкап: `deploy/backup/backup.sh` по cron. Обновление: `deploy/scripts/deploy.sh`.
