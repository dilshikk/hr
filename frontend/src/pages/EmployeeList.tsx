import { useState } from "react";
import { api } from "../api";
import { useLoad } from "../hooks/useLoad";
import { canEditEmployee, ROLE_LABELS, type Employee, type Me } from "../types";
import EmployeeEdit from "./EmployeeEdit";

export default function EmployeeList({ me }: { me: Me }) {
  const employees = useLoad(api.employees, "Не удалось загрузить сотрудников");
  const branches = useLoad(api.branches, "Не удалось загрузить филиалы");
  const [editing, setEditing] = useState<Employee | null>(null);

  const branchName = (id: number | null) =>
    id === null ? "Без филиала" : branches.data?.find((b) => b.id === id)?.name ?? "—";

  if (editing && branches.data) {
    return (
      <EmployeeEdit
        me={me}
        employee={editing}
        branches={branches.data}
        onDone={(updated) => {
          employees.setData((employees.data ?? []).map((e) => (e.id === updated.id ? updated : e)));
          setEditing(null);
        }}
        onCancel={() => setEditing(null)}
      />
    );
  }

  return (
    <section>
      <h1>Сотрудники</h1>
      <p className="muted small">
        Новые сотрудники появляются здесь после первого входа через бота, с правом «Только просмотр».
      </p>

      {employees.error && <p className="error">{employees.error}</p>}
      {!employees.error && employees.data === null && <p className="muted">Загрузка…</p>}

      <ul className="list">
        {employees.data?.map((e) => {
          const editable = canEditEmployee(me, e);
          return (
            <li key={e.id}>
              <button className="item" disabled={!editable} onClick={() => setEditing(e)}>
                <span className="item-main">
                  <span className="item-name">
                    {e.full_name || `ID ${e.telegram_id}`}
                    {e.id === me.id && " (вы)"}
                  </span>
                  <span className="muted small">{ROLE_LABELS[e.role] ?? e.role} · {branchName(e.branch_id)}</span>
                </span>
                {!e.is_active && <span className="badge stage-rejected">Заблокирован</span>}
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
