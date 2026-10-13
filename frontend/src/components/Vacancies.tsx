import { useEffect, useState } from "react";
import { api } from "../api";
import { CAN_WRITE_VACANCIES, type Me, type Vacancy } from "../types";

export default function Vacancies({ me }: { me: Me }) {
  const [items, setItems] = useState<Vacancy[] | null>(null);
  const [error, setError] = useState("");
  const [title, setTitle] = useState("");
  const [branch, setBranch] = useState(me.branch_id?.toString() ?? "");
  const canWrite = CAN_WRITE_VACANCIES.includes(me.role);

  const load = async () => {
    try {
      setItems(await api.get<Vacancy[]>("/vacancies"));
      setError("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка");
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const add = async () => {
    if (!title.trim() || !branch) return setError("Укажите название и номер филиала");
    try {
      await api.post("/vacancies", { title, branch_id: Number(branch) });
      setTitle("");
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка");
    }
  };

  return (
    <section>
      {error && <p className="error">{error}</p>}
      {canWrite && (
        <div className="card form">
          <input placeholder="Название вакансии" value={title} onChange={(e) => setTitle(e.target.value)} />
          <input placeholder="Номер филиала" inputMode="numeric" value={branch} onChange={(e) => setBranch(e.target.value)} />
          <button onClick={add}>Создать</button>
        </div>
      )}
      {items === null && <p className="muted">Загрузка...</p>}
      {items?.length === 0 && <p className="muted">Вакансий нет</p>}
      {items?.map((v) => (
        <div className="card" key={v.id}>
          <b>{v.title}</b>
          <div className="muted">филиал {v.branch_id} · {v.status}</div>
        </div>
      ))}
    </section>
  );
}
