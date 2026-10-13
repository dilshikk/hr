#!/usr/bin/env bash
# Обновление на VPS: код, зависимости, миграции, перезапуск.
set -euo pipefail
cd /opt/mado_jbot
git pull --ff-only
.venv/bin/pip install -e .
.venv/bin/alembic upgrade head
sudo systemctl restart mado-api mado-bot
curl -fsS http://127.0.0.1:8000/health/live && echo " OK"
