import { useCallback, useEffect, useState } from "react";
import { api } from "../../services/api";
import { useBranches } from "../../hooks/useBranches";
import BranchSelect from "../../components/BranchSelect";
import { CAN_WRITE_VACANCIES, type Me, type Vacancy } from "../../types";

export default function Vacancies({ me }: { me: Me }) {
  const branches = useBranches();
  const [items, setItems] = useState<Vacancy[] | null>(null);
  const [error, setError] = useState("");
  const [title, setTitle] = useState("");
  const [branch, setBranch] = useState(me.branch_id?.toString() ?? "");
  const canWrite = CAN_WRITE_VACANCIES.includes(me.role);
  const fail = (e: unknown) => setError(e instanceof Error ? e.message : "Ошибка");

  const load = useCallback(async () => {
    try {
      setItems(await api.get<Vacancy[]>("/vacancies"));
      setError("");
    } catch (e) {
      fail(e);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const add = async () => {
    if (!title.trim() || !branch) return setError("Укажите название и филиал");
    try {
      await api.post("/vacancies", { title, branch_id: Number(branch) });
      setTitle("");
      await load();
    } catch (e) {
      fail(e);
    }
  };

  return (
    <section>
      {error && <p className="error">{error}</p>}
      {canWrite && (
        <div className="card form">
          <input placeholder="Название вакансии" value={title} onChange={(e) => setTitle(e.target.value)} />
          <BranchSelect branches={branches} value={branch} onChange={setBranch} />
          <button onClick={add}>Создать</button>
        </div>
      )}
      {items === null && <p className="muted">Загрузка...</p>}
      {items?.length === 0 && <p className="muted">Вакансий нет</p>}
      {items?.map((v) => (
        <div className="card" key={v.id}>
          <b>{v.title}</b>
          <div className="muted">{branches.find((b) => b.id === v.branch_id)?.name ?? `филиал ${v.branch_id}`} · {v.status}</div>
        </div>
      ))}
    </section>
  );
}
