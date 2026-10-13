import { useState, type FormEvent } from "react";
import { api, errorText } from "../api";
import { useLoad } from "../hooks/useLoad";
import { haptic } from "../telegram";
import type { Branch, Vacancy } from "../types";

const STATUS_LABELS: Record<string, string> = { draft: "Черновик", open: "Открыта", closed: "Закрыта" };

// Совпадает с backend/app/services/vacancy.py
const STATUS_ACTIONS: Record<string, { to: string; label: string }[]> = {
  draft: [{ to: "open", label: "Открыть" }, { to: "closed", label: "Закрыть" }],
  open: [{ to: "closed", label: "Закрыть" }],
  closed: [{ to: "open", label: "Открыть снова" }],
};

export default function VacancyList() {
  const vacancies = useLoad(api.vacancies, "Не удалось загрузить вакансии");
  const branches = useLoad(api.branches, "Не удалось загрузить филиалы");
  const [adding, setAdding] = useState(false);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const branchName = (id: number) => branches.data?.find((b) => b.id === id)?.name ?? "—";

  async function changeStatus(v: Vacancy, to: string) {
    setBusyId(v.id);
    setError(null);
    try {
      const updated = await api.setVacancyStatus(v.id, to);
      vacancies.setData((vacancies.data ?? []).map((x) => (x.id === updated.id ? updated : x)));
      haptic("success");
    } catch (e: unknown) {
      haptic("error");
      setError(errorText(e, "Не удалось сменить статус"));
    } finally {
      setBusyId(null);
    }
  }

  return (
    <section>
      <header className="row between">
        <h1>Вакансии</h1>
        {!adding && <button className="btn" onClick={() => setAdding(true)}>+ Добавить</button>}
      </header>

      {adding && branches.data && (
        <VacancyForm
          branches={branches.data}
          onDone={(v) => {
            vacancies.setData([v, ...(vacancies.data ?? [])]);
            setAdding(false);
          }}
          onCancel={() => setAdding(false)}
        />
      )}

      {(vacancies.error || error) && <p className="error">{vacancies.error ?? error}</p>}
      {!vacancies.error && vacancies.data === null && <p className="muted">Загрузка…</p>}
      {vacancies.data?.length === 0 && !adding && <p className="muted center-text">Вакансий пока нет</p>}

      <ul className="list">
        {vacancies.data?.map((v) => (
          <li key={v.id} className="item static column">
            <span className="row between full">
              <span className="item-main">
                <span className="item-name">{v.title}</span>
                <span className="muted small">{branchName(v.branch_id)}</span>
              </span>
              <span className={v.status === "open" ? "badge stage-hired" : "badge"}>{STATUS_LABELS[v.status] ?? v.status}</span>
            </span>
            <span className="row">
              {(STATUS_ACTIONS[v.status] ?? []).map((a) => (
                <button
                  key={a.to}
                  className={a.to === "closed" ? "chip" : "chip active"}
                  disabled={busyId === v.id}
                  onClick={() => changeStatus(v, a.to)}
                >
                  {a.label}
                </button>
              ))}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}

type FormProps = { branches: Branch[]; onDone: (v: Vacancy) => void; onCancel: () => void };

function VacancyForm({ branches, onDone, onCancel }: FormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [branchId, setBranchId] = useState<number | null>(branches[0]?.id ?? null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!title.trim() || branchId === null) return;
    setBusy(true);
    setError(null);
    try {
      const v = await api.createVacancy({ title: title.trim(), branch_id: branchId, description: description.trim() });
      haptic("success");
      onDone(v);
    } catch (err: unknown) {
      haptic("error");
      setError(errorText(err, "Не удалось сохранить вакансию"));
    } finally {
      setBusy(false);
    }
  }

  if (branches.length === 0) {
    return <p className="error">Сначала создайте филиал на вкладке «Филиалы»</p>;
  }

  return (
    <form className="stack panel" onSubmit={submit}>
      <label>
        Название
        <input value={title} maxLength={200} required placeholder="Бариста" onChange={(e) => setTitle(e.target.value)} />
      </label>
      <label>
        Филиал
        <select value={branchId ?? ""} onChange={(e) => setBranchId(Number(e.target.value))}>
          {branches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
        </select>
      </label>
      <label>
        Описание
        <textarea value={description} maxLength={5000} placeholder="График, обязанности, условия" onChange={(e) => setDescription(e.target.value)} />
      </label>
      <p className="muted small">Вакансия создаётся черновиком. Откройте её, чтобы к ней можно было добавлять кандидатов.</p>
      {error && <p className="error">{error}</p>}
      <button className="btn" type="submit" disabled={busy || !title.trim()}>{busy ? "Сохранение…" : "Сохранить"}</button>
      <button className="btn ghost" type="button" onClick={onCancel}>Отмена</button>
    </form>
  );
}
