import { useEffect, useState } from "react";
import { api, ApiError } from "../api";
import { canWrite, STAGE_LABELS, type Candidate, type Me, type Stage } from "../types";

type Props = { me: Me; onOpen: (id: number) => void; onNew: () => void };

const FILTERS: (Stage | "")[] = ["", "new", "review", "contact", "interview", "trial", "offer", "reserve", "hired", "rejected"];

export default function CandidateList({ me, onOpen, onNew }: Props) {
  const [stage, setStage] = useState<Stage | "">("");
  const [items, setItems] = useState<Candidate[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setItems(null);
    setError(null);
    api.candidates(stage)
      .then(setItems)
      .catch((e: unknown) => setError(e instanceof ApiError ? e.message : "Не удалось загрузить список"));
  }, [stage]);

  return (
    <section>
      <header className="row between">
        <div>
          <h1>Кандидаты</h1>
          <p className="muted small">{me.name}</p>
        </div>
        {canWrite(me.role) && <button className="btn" onClick={onNew}>+ Добавить</button>}
      </header>

      <div className="chips">
        {FILTERS.map((s) => (
          <button key={s || "all"} className={s === stage ? "chip active" : "chip"} onClick={() => setStage(s)}>
            {s ? STAGE_LABELS[s] : "Все"}
          </button>
        ))}
      </div>

      {error && <p className="error">{error}</p>}
      {!error && items === null && <p className="muted">Загрузка…</p>}
      {items?.length === 0 && (
        <p className="muted center-text">
          {me.role !== "owner" && me.role !== "hr_admin" && me.branch_id === null
            ? "Вам ещё не назначен филиал. Обратитесь к HR-администратору"
            : "Здесь пока никого нет"}
        </p>
      )}

      <ul className="list">
        {items?.map((c) => (
          <li key={c.id}>
            <button className="item" onClick={() => onOpen(c.id)}>
              <span className="item-name">{c.full_name}</span>
              <span className={`badge stage-${c.stage}`}>{STAGE_LABELS[c.stage]}</span>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
