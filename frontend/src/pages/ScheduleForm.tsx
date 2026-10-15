import { useState } from "react";
import { api, errorText } from "../api";
import { useLoad } from "../hooks/useLoad";
import { ROLE_LABELS, canWrite } from "../types";

type Props = { onDone: () => void; onCancel: () => void };

const DURATIONS = [15, 30, 45, 60, 90];
// Время вводится по Ташкенту (UTC+5, без перехода на летнее время), независимо от часового пояса телефона.
const toIso = (local: string) => new Date(`${local}:00+05:00`).toISOString();

/** Форма назначения интервью. */
export default function ScheduleForm({ onDone, onCancel }: Props) {
  const candidates = useLoad(() => api.candidates(""), "Не удалось загрузить кандидатов");
  const employees = useLoad(api.employees, "Не удалось загрузить сотрудников");
  const [candidateId, setCandidateId] = useState("");
  const [interviewerId, setInterviewerId] = useState("");
  const [when, setWhen] = useState("");
  const [duration, setDuration] = useState(30);
  const [format, setFormat] = useState<"offline" | "online">("offline");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const interviewers = employees.data?.filter((e) => e.is_active && canWrite(e.role)) ?? [];
  const loadError = candidates.error ?? employees.error;
  const ready = candidateId && interviewerId && when && !busy;

  const submit = () => {
    setBusy(true);
    setError(null);
    api.createInterview({
      candidate_id: Number(candidateId),
      interviewer_id: Number(interviewerId),
      starts_at: toIso(when),
      duration_min: duration,
      format,
    })
      .then(onDone)
      .catch((e: unknown) => setError(errorText(e, "Не удалось назначить интервью")))
      .finally(() => setBusy(false));
  };

  return (
    <section className="stack">
      <h1>Новое интервью</h1>
      {loadError && <p className="error">{loadError}</p>}
      <label>
        Кандидат
        <select value={candidateId} onChange={(e) => setCandidateId(e.target.value)}>
          <option value="">Выберите</option>
          {candidates.data?.map((c) => <option key={c.id} value={c.id}>{c.full_name}</option>)}
        </select>
      </label>
      <label>
        Интервьюер
        <select value={interviewerId} onChange={(e) => setInterviewerId(e.target.value)}>
          <option value="">Выберите</option>
          {interviewers.map((e) => (
            <option key={e.id} value={e.id}>{e.full_name} ({ROLE_LABELS[e.role] ?? e.role})</option>
          ))}
        </select>
      </label>
      <label>
        Дата и время (Ташкент)
        <input type="datetime-local" value={when} onChange={(e) => setWhen(e.target.value)} />
      </label>
      <label>
        Длительность
        <select value={duration} onChange={(e) => setDuration(Number(e.target.value))}>
          {DURATIONS.map((d) => <option key={d} value={d}>{d} мин</option>)}
        </select>
      </label>
      <label>
        Формат
        <select value={format} onChange={(e) => setFormat(e.target.value === "online" ? "online" : "offline")}>
          <option value="offline">В офисе</option>
          <option value="online">Онлайн</option>
        </select>
      </label>
      {error && <p className="error">{error}</p>}
      <div className="row">
        <button className="btn grow" disabled={!ready} onClick={submit}>Назначить</button>
        <button className="btn ghost" disabled={busy} onClick={onCancel}>Отмена</button>
      </div>
    </section>
  );
}
