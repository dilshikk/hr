import { useCallback, useEffect, useState } from "react";
import { api, errorText, type AuditEntry } from "../api";

const PAGE = 50;

// Известные действия на человеческом языке; остальные показываем как есть.
const ACTION_LABELS: Record<string, string> = {
  "login.2fa_required": "Вход: нужен код 2FA",
  "login.2fa_failed": "Вход: неверный код 2FA",
  "2fa.setup": "2FA: начата настройка",
  "2fa.enabled": "2FA: включена",
  "2fa.confirm_failed": "2FA: неверный код при настройке",
  "2fa.reset": "2FA: сброшена",
  "employee.update": "Сотрудник изменён",
};

const label = (action: string) => ACTION_LABELS[action] ?? action;

/** Время показываем в часовом поясе пользователя; на сервере оно хранится в UTC. */
const formatTime = (iso: string) =>
  new Date(iso).toLocaleString("ru-RU", { dateStyle: "short", timeStyle: "short" });

/** Журнал действий: новые записи сверху, фильтр по типу, подгрузка по 50. */
export default function AuditLog() {
  const [action, setAction] = useState("");
  const [items, setItems] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [hasMore, setHasMore] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback((filter: string, offset: number) => {
    setLoading(true);
    setError(null);
    api.audit(filter, offset, PAGE)
      .then((page) => {
        setItems((prev) => (offset === 0 ? page : [...prev, ...page]));
        setHasMore(page.length === PAGE);
      })
      .catch((e: unknown) => setError(errorText(e, "Не удалось загрузить журнал")))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => load(action, 0), [action, load]);

  return (
    <section>
      <h1>Журнал действий</h1>
      <label>
        Тип действия
        <select value={action} onChange={(e) => setAction(e.target.value)}>
          <option value="">Все</option>
          {Object.entries(ACTION_LABELS).map(([id, text]) => (
            <option key={id} value={id}>{text}</option>
          ))}
        </select>
      </label>

      {error && (
        <div className="stack panel">
          <p className="error">{error}</p>
          <button className="btn ghost" onClick={() => load(action, items.length)}>Повторить</button>
        </div>
      )}
      {!error && !loading && items.length === 0 && <p className="muted center-text">Записей пока нет</p>}

      <ul className="list">
        {items.map((e) => (
          <li key={e.id} className="item column static">
            <div className="row between">
              <span>{label(e.action)}</span>
              <span className="muted small">{formatTime(e.created_at)}</span>
            </div>
            <span className="muted small">
              {e.actor_name ?? "Система"}{e.target ? `: ${e.target}` : ""}
            </span>
          </li>
        ))}
      </ul>

      {loading && <p className="muted center-text">Загрузка…</p>}
      {!loading && !error && hasMore && (
        <button className="btn ghost full panel" onClick={() => load(action, items.length)}>Показать ещё</button>
      )}
    </section>
  );
}
