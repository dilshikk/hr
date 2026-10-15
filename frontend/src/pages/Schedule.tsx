import { useState } from "react";
import { api, errorText, type ScheduledInterview, type ScheduleStatus } from "../api";
import { useLoad } from "../hooks/useLoad";
import ScheduleForm from "./ScheduleForm";
import ScoreForm from "./ScoreForm";

const TZ = "Asia/Tashkent";
const FILTERS: { id: ScheduleStatus; label: string }[] = [
  { id: "scheduled", label: "Предстоящие" },
  { id: "done", label: "Проведённые" },
  { id: "cancelled", label: "Отменённые" },
];
const FORMAT_LABELS = { offline: "В офисе", online: "Онлайн" };

const fmtDay = (iso: string) =>
  new Date(iso).toLocaleDateString("ru-RU", { timeZone: TZ, weekday: "short", day: "numeric", month: "long" });
const fmtTime = (iso: string) =>
  new Date(iso).toLocaleTimeString("ru-RU", { timeZone: TZ, hour: "2-digit", minute: "2-digit" });

function groupByDay(items: ScheduledInterview[]): [string, ScheduledInterview[]][] {
  const groups = new Map<string, ScheduledInterview[]>();
  for (const i of items) {
    const key = fmtDay(i.starts_at);
    groups.set(key, [...(groups.get(key) ?? []), i]);
  }
  return [...groups];
}

type RowProps = { item: ScheduledInterview; onChanged: () => void };

function InterviewRow({ item, onChanged }: RowProps) {
  const [scoring, setScoring] = useState(false);
  const [confirmCancel, setConfirmCancel] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cancel = () => {
    api.cancelInterview(item.id)
      .then(onChanged)
      .catch((e: unknown) => setError(errorText(e, "Не удалось отменить интервью")));
  };

  return (
    <li className="item column static">
      <div className="row between">
        <span className="item-name">{item.candidate_name}</span>
        <span className="badge">{fmtTime(item.starts_at)}, {item.duration_min} мин</span>
      </div>
      <span className="muted small">
        Интервьюер: {item.interviewer_name}. {FORMAT_LABELS[item.format]}
      </span>
      {item.status === "done" && (
        <span className="small">Оценка: {item.score}/5{item.comment ? `. ${item.comment}` : ""}</span>
      )}
      {error && <p className="error small">{error}</p>}
      {item.status === "scheduled" && !scoring && (
        <div className="row">
          <button className="btn grow" onClick={() => setScoring(true)}>Оценить</button>
          {confirmCancel ? (
            <button className="btn danger" onClick={cancel}>Точно отменить?</button>
          ) : (
            <button className="btn ghost" onClick={() => setConfirmCancel(true)}>Отменить</button>
          )}
        </div>
      )}
      {scoring && <ScoreForm id={item.id} onDone={onChanged} onCancel={() => setScoring(false)} />}
    </li>
  );
}

function ScheduleList({ status }: { status: ScheduleStatus }) {
  const list = useLoad(() => api.schedule(status), "Не удалось загрузить календарь");
  return (
    <>
      {list.error && (
        <div className="stack panel">
          <p className="error">{list.error}</p>
          <button className="btn ghost" onClick={list.reload}>Повторить</button>
        </div>
      )}
      {!list.error && list.data === null && <p className="muted">Загрузка…</p>}
      {list.data?.length === 0 && <p className="muted center-text">Здесь пока ничего нет</p>}
      {list.data && groupByDay(list.data).map(([day, rows]) => (
        <div key={day}>
          <h2>{day}</h2>
          <ul className="list">
            {rows.map((i) => <InterviewRow key={i.id} item={i} onChanged={list.reload} />)}
          </ul>
        </div>
      ))}
    </>
  );
}

/** Календарь интервью: список по дням, назначение, отмена и оценка. */
export default function Schedule() {
  const [status, setStatus] = useState<ScheduleStatus>("scheduled");
  const [creating, setCreating] = useState(false);
  // key заставляет список перезагрузиться после создания интервью.
  const [version, setVersion] = useState(0);

  if (creating) {
    return (
      <ScheduleForm
        onDone={() => {
          setCreating(false);
          setStatus("scheduled");
          setVersion((v) => v + 1);
        }}
        onCancel={() => setCreating(false)}
      />
    );
  }

  return (
    <section>
      <div className="row between">
        <h1>Календарь</h1>
        <button className="btn" onClick={() => setCreating(true)}>Назначить</button>
      </div>
      <p className="muted small">Время указано по Ташкенту</p>
      <div className="chips">
        {FILTERS.map((f) => (
          <button key={f.id} className={f.id === status ? "chip active" : "chip"} onClick={() => setStatus(f.id)}>
            {f.label}
          </button>
        ))}
      </div>
      <ScheduleList key={`${status}-${version}`} status={status} />
    </section>
  );
}
