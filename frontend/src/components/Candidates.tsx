import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import { CAN_WRITE, NEXT, STAGES, type Candidate, type Me } from "../types";

export default function Candidates({ me }: { me: Me }) {
  const [items, setItems] = useState<Candidate[] | null>(null);
  const [stage, setStage] = useState("");
  const [error, setError] = useState("");
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [branch, setBranch] = useState(me.branch_id?.toString() ?? "");
  const canWrite = CAN_WRITE.includes(me.role);

  const load = useCallback(async () => {
    try {
      const q = stage ? `?stage=${stage}` : "";
      setItems(await api.get<Candidate[]>(`/candidates${q}`));
      setError("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка");
    }
  }, [stage]);

  useEffect(() => {
    void load();
  }, [load]);

  const add = async () => {
    if (!name.trim() || !branch) return setError("Укажите имя и номер филиала");
    try {
      await api.post("/candidates", { full_name: name, phone: phone || null, branch_id: Number(branch) });
      setName("");
      setPhone("");
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка");
    }
  };

  const move = async (c: Candidate, to: string) => {
    let reason = "";
    if (to === "rejected") {
      reason = window.prompt("Причина отказа")?.trim() ?? "";
      if (!reason) return setError("Для отказа нужна причина");
    }
    try {
      await api.post(`/candidates/${c.id}/stage`, { stage: to, reason });
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка");
    }
  };

  return (
    <section>
      <select value={stage} onChange={(e) => setStage(e.target.value)}>
        <option value="">Все этапы</option>
        {Object.entries(STAGES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
      </select>
      {error && <p className="error">{error}</p>}
      {canWrite && (
        <div className="card form">
          <input placeholder="Имя кандидата" value={name} onChange={(e) => setName(e.target.value)} />
          <input placeholder="Телефон" value={phone} onChange={(e) => setPhone(e.target.value)} />
          <input placeholder="Номер филиала" inputMode="numeric" value={branch} onChange={(e) => setBranch(e.target.value)} />
          <button onClick={add}>Добавить</button>
        </div>
      )}
      {items === null && <p className="muted">Загрузка...</p>}
      {items?.length === 0 && <p className="muted">Кандидатов нет</p>}
      {items?.map((c) => (
        <div className="card" key={c.id}>
          <b>{c.full_name}</b>
          <div className="muted">{c.phone ?? "без телефона"} · филиал {c.branch_id}</div>
          <span className="badge">{STAGES[c.stage] ?? c.stage}</span>
          {canWrite && (
            <div className="row">
              {(NEXT[c.stage] ?? []).map((to) => (
                <button key={to} className="small" onClick={() => move(c, to)}>{STAGES[to]}</button>
              ))}
            </div>
          )}
        </div>
      ))}
    </section>
  );
}
