# Перенос на VPS

## 1. Обследование
- ОС, ресурсы, место, порты, домены, firewall
- Инвентаризация systemd, PM2, Nginx, Docker, PostgreSQL/SQLite, логов
- Убедиться, что нет второго polling-процесса того же бота
- Зафиксировать пути, права, env, процедуру отката

## 2. Backup
- Зафиксировать commit и конфигурацию (без секретов)
- Сохранить БД и пользовательские файлы, проверить читаемость
- SQLite — согласованный backup; PostgreSQL — `pg_dump`
- Сохранить конфигурации Nginx/systemd

## 3. Установка (Ubuntu/Debian, после проверки ОС)
```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip build-essential nginx certbot python3-certbot-nginx postgresql postgresql-contrib
cd /opt
sudo git clone https://github.com/dilshikk/mado_jbot.git
sudo chown -R $USER:$USER /opt/mado_jbot
cd /opt/mado_jbot
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip wheel
pip install -r requirements.txt
```
Если PostgreSQL уже обслуживает другие проекты — не переустанавливать; создать отдельную БД и пользователя.

## 4. Конфигурация
- Отдельный `.env` с минимальными правами (`/etc/mado-jbot/mado-jbot.env`)
- Не коммитить `.env`, `credentials.json`, дампы, ключи
- Домен и HTTPS — до подключения Mini App

## 5. Тесты и миграции
```bash
pytest -q
alembic upgrade head
python main.py
```
Выбрать один механизм схемы (init_db или Alembic). Миграции на production — только после backup.

## 6. systemd
См. `deploy/mado-jbot.service`. Не запускать от root.
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now mado-jbot
systemctl status mado-jbot && journalctl -u mado-jbot -f
```

## 7. Mini App / HTTPS
Статика frontend через Nginx, `/api/` проксировать на backend, БД наружу не открывать, TLS с автопродлением, домен Web App в BotFather, проверка CSP/CORS.

## 8. Мониторинг
Статус процессов, ротация логов (без токенов и 2FA-кодов), проверка БД/API/backup, оповещение админа, еженедельный тест восстановления.
