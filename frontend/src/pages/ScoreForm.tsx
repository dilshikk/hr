import { useState } from "react";
import { api, errorText } from "../api";

type Props = { id: number; onDone: () => void; onCancel: () => void };

/** Оценка проведённого интервью: от 1 до 5 и короткий комментарий. */
export default function ScoreForm({ id, onDone, onCancel }: Props) {
  const [score, setScore] = useState(4);
  const [comment, setComment] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = () => {
    setBusy(true);
    setError(null);
    api.scoreInterview(id, score, comment.trim())
      .then(onDone)
      .catch((e: unknown) => setError(errorText(e, "Не удалось сохранить оценку")))
      .finally(() => setBusy(false));
  };

  return (
    <div className="stack">
      <div className="chips">
        {[1, 2, 3, 4, 5].map((n) => (
          <button key={n} className={n === score ? "chip active" : "chip"} onClick={() => setScore(n)}>{n}</button>
        ))}
      </div>
      <textarea placeholder="Комментарий" maxLength={500} value={comment} onChange={(e) => setComment(e.target.value)} />
      {error && <p className="error small">{error}</p>}
      <div className="row">
        <button className="btn grow" disabled={busy} onClick={submit}>Сохранить оценку</button>
        <button className="btn ghost" disabled={busy} onClick={onCancel}>Закрыть</button>
      </div>
    </div>
  );
}
