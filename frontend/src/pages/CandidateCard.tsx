import { useEffect, useState } from "react";
import { api, ApiError } from "../api";
import { haptic } from "../telegram";
import { canWrite, STAGE_LABELS, TRANSITIONS, type Candidate, type Me, type Stage } from "../types";

type Props = { id: number; me: Me; onBack: () => void };

export default function CandidateCard({ id, me, onBack }: Props) {
  const [cand, setCand] = useState<Candidate | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [rejecting, setRejecting] = useState(false);
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);

  const load = () =>
    api.candidate(id)
      .then(setCand)
      .catch((e: unknown) => setError(e instanceof ApiError ? e.message : "Не удалось загрузить карточку"));

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function move(stage: Stage) {
    if (!cand) return;
    setBusy(true);
    setError(null);
    try {
      setCand(await api.moveStage(cand.id, stage, stage === "rejected" ? reason.trim() : ""));
      setRejecting(false);
      setReason("");
      haptic("success");
    } catch (e: unknown) {
      haptic("error");
      setError(e instanceof ApiError ? e.message : "Не удалось сменить этап");
      // Этап мог изменить другой сотрудник — показываем актуальное состояние.
      if (e instanceof ApiError && e.status === 409) await load();
    } finally {
      setBusy(false);
    }
  }

  if (!cand) {
    return (
      <section>
        {error ? <p className="error">{error}</p> : <p className="muted">Загрузка…</p>}
        <button className="btn ghost" onClick={onBack}>К списку</button>
      </section>
    );
  }

  const next = canWrite(me.role) ? TRANSITIONS[cand.stage] : [];

  return (
    <section>
      <h1>{cand.full_name}</h1>
      <span className={`badge stage-${cand.stage}`}>{STAGE_LABELS[cand.stage]}</span>

      <dl className="details">
        <dt>Телефон</dt>
        <dd>{cand.phone ? <a href={`tel:${cand.phone}`}>{cand.phone}</a> : "—"}</dd>
      </dl>

      {error && <p className="error">{error}</p>}

      {next.length > 0 && !rejecting && (
        <div className="stack">
          <h2>Перевести на этап</h2>
          {next.map((s) => (
            <button
              key={s}
              className={s === "rejected" ? "btn danger" : "btn"}
              disabled={busy}
              onClick={() => (s === "rejected" ? setRejecting(true) : move(s))}
            >
              {STAGE_LABELS[s]}
            </button>
          ))}
        </div>
      )}

      {rejecting && (
        <div className="stack">
          <h2>Причина отказа</h2>
          <textarea
            value={reason}
            maxLength={300}
            placeholder="Например: не подошёл график"
            onChange={(e) => setReason(e.target.value)}
          />
          <button className="btn danger" disabled={busy || !reason.trim()} onClick={() => move("rejected")}>
            Подтвердить отказ
          </button>
          <button className="btn ghost" onClick={() => setRejecting(false)}>Отмена</button>
        </div>
      )}

      {next.length === 0 && canWrite(me.role) && <p className="muted">Этап завершён, дальнейших шагов нет</p>}
    </section>
  );
}
