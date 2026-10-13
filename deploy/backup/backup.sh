#!/usr/bin/env bash
# Резервная копия PostgreSQL. Запускать по cron, копии хранить вне сервера и шифровать.
set -euo pipefail
OUT="${BACKUP_DIR:-/var/backups/mado-hr}"
mkdir -p "$OUT"
pg_dump "$DATABASE_URL_SYNC" | gzip > "$OUT/mado-hr-$(date +%F-%H%M).sql.gz"
find "$OUT" -name '*.sql.gz' -mtime +14 -delete
