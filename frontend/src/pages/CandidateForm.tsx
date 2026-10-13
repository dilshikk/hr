import { useEffect, useState, type FormEvent } from "react";
import { api, ApiError } from "../api";
import { haptic } from "../telegram";
import type { Branch, Me, Vacancy } from "../types";

type Props = { me: Me; onDone: (id: number) => void; onCancel: () => void };

export default function CandidateForm({ me, onDone, onCancel }: Props) {
  const [branches, setBranches] = useState<Branch[]>([]);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [branchId, setBranchId] = useState<number | null>(me.branch_id);
  const [vacancyId, setVacancyId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    Promise.all([api.branches(), api.vacancies()])
      .then(([b, v]) => {
        setBranches(b);
        setVacancies(v);
        if (me.branch_id === null && b.length > 0) setBranchId(b[0].id);
      })
      .catch(() => setError("Не удалось загрузить филиалы"));
  }, [me.branch_id]);

  // Только вакансии выбранного филиала — сервер другие всё равно отклонит.
  const branchVacancies = vacancies.filter((v) => v.branch_id === branchId);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!name.trim() || branchId === null) return;
    setBusy(true);
    setError(null);
    try {
      const c = await api.createCandidate({
        full_name: name.trim(),
        phone: phone.trim() || null,
        branch_id: branchId,
        vacancy_id: vacancyId,
      });
      haptic("success");
      onDone(c.id);
    } catch (err: unknown) {
      haptic("error");
      setError(err instanceof ApiError ? err.message : "Не удалось сохранить");
    } finally {
      setBusy(false);
    }
  }

  const canPickBranch = me.role === "owner" || me.role === "hr_admin";

  return (
    <form className="stack" onSubmit={submit}>
      <h1>Новый кандидат</h1>

      <label>
        Имя и фамилия
        <input value={name} maxLength={200} required placeholder="Алишер Каримов" onChange={(e) => setName(e.target.value)} />
      </label>

      <label>
        Телефон
        <input value={phone} maxLength={32} inputMode="tel" placeholder="+998 90 123 45 67" onChange={(e) => setPhone(e.target.value)} />
      </label>

      {canPickBranch && (
        <label>
          Филиал
          <select
            value={branchId ?? ""}
            onChange={(e) => {
              setBranchId(Number(e.target.value));
              setVacancyId(null);
            }}
          >
            {branches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
          </select>
        </label>
      )}

      <label>
        Вакансия
        <select value={vacancyId ?? ""} onChange={(e) => setVacancyId(e.target.value ? Number(e.target.value) : null)}>
          <option value="">Без вакансии</option>
          {branchVacancies.map((v) => <option key={v.id} value={v.id}>{v.title}</option>)}
        </select>
      </label>

      {branchId === null && <p className="error">Сначала нужен хотя бы один филиал</p>}
      {error && <p className="error">{error}</p>}

      <button className="btn" type="submit" disabled={busy || !name.trim() || branchId === null}>
        {busy ? "Сохранение…" : "Сохранить"}
      </button>
      <button className="btn ghost" type="button" onClick={onCancel}>Отмена</button>
    </form>
  );
}
