import { useState, type FormEvent } from "react";
import { api, errorText } from "../api";
import { useLoad } from "../hooks/useLoad";
import { haptic } from "../telegram";
import { isOwner, type Me } from "../types";

export default function BranchList({ me }: { me: Me }) {
  const branches = useLoad(api.branches, "Не удалось загрузить филиалы");
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setBusy(true);
    setError(null);
    try {
      const b = await api.createBranch(name.trim());
      branches.setData([...(branches.data ?? []), b].sort((a, c) => a.name.localeCompare(c.name, "ru")));
      setName("");
      haptic("success");
    } catch (err: unknown) {
      haptic("error");
      setError(errorText(err, "Не удалось создать филиал"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section>
      <h1>Филиалы</h1>

      {isOwner(me.role) ? (
        <form className="row panel" onSubmit={submit}>
          <input className="grow" value={name} maxLength={120} placeholder="Новый филиал, например «Чиланзар»" onChange={(e) => setName(e.target.value)} />
          <button className="btn" type="submit" disabled={busy || !name.trim()}>Добавить</button>
        </form>
      ) : (
        <p className="muted small">Создавать филиалы может только владелец</p>
      )}
      {error && <p className="error">{error}</p>}

      {branches.error && <p className="error">{branches.error}</p>}
      {!branches.error && branches.data === null && <p className="muted">Загрузка…</p>}
      {branches.data?.length === 0 && <p className="muted center-text">Филиалов пока нет</p>}

      <ul className="list">
        {branches.data?.map((b) => (
          <li key={b.id} className="item static">
            <span className="item-name">{b.name}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
