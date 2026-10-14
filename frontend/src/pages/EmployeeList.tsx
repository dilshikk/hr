import { useState } from "react";
import { api } from "../api";
import { useLoad } from "../hooks/useLoad";
import { ROLE_LABELS, type Employee, type Me } from "../types";
import EmployeeCard from "./EmployeeCard";
import EmployeeEdit from "./EmployeeEdit";

type View = { name: "card"; employee: Employee } | { name: "edit"; employee: Employee };

export default function EmployeeList({ me }: { me: Me }) {
  const employees = useLoad(api.employees, "Не удалось загрузить сотрудников");
  const branches = useLoad(api.branches, "Не удалось загрузить филиалы");
  const [view, setView] = useState<View | null>(null);

  const branchName = (id: number | null) =>
    id === null ? "Без филиала" : branches.data?.find((b) => b.id === id)?.name ?? "—";

  if (view?.name === "edit" && branches.data) {
    return (
      <EmployeeEdit
        me={me}
        employee={view.employee}
        branches={branches.data}
        onDone={(updated) => {
          employees.setData((employees.data ?? []).map((e) => (e.id === updated.id ? updated : e)));
          setView({ name: "card", employee: updated });
        }}
        onCancel={() => setView({ name: "card", employee: view.employee })}
      />
    );
  }

  if (view?.name === "card") {
    return (
      <EmployeeCard
        me={me}
        employee={view.employee}
        branchName={branchName(view.employee.branch_id)}
        onEdit={() => setView({ name: "edit", employee: view.employee })}
        onBack={() => setView(null)}
      />
    );
  }

  return (
    <section>
      <h1>Сотрудники</h1>
      <p className="muted small">
        Новые сотрудники появляются здесь после первого входа через бота, с правом «Только просмотр». Нажмите на сотрудника, чтобы открыть карточку.
      </p>

      {employees.error && <p className="error">{employees.error}</p>}
      {!employees.error && employees.data === null && <p className="muted">Загрузка…</p>}

      <ul className="list">
        {employees.data?.map((e) => (
          <li key={e.id}>
            <button className="item" onClick={() => setView({ name: "card", employee: e })}>
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
        ))}
      </ul>
    </section>
  );
}
