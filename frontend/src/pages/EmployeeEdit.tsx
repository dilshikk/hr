import { useState } from "react";
import { api, errorText } from "../api";
import { haptic } from "../telegram";
import { assignableRoles, ROLE_LABELS, type Branch, type Employee, type Me } from "../types";

type Props = {
  me: Me;
  employee: Employee;
  branches: Branch[];
  onDone: (e: Employee) => void;
  onCancel: () => void;
};

export default function EmployeeEdit({ me, employee, branches, onDone, onCancel }: Props) {
  const [role, setRole] = useState(employee.role);
  const [branchId, setBranchId] = useState<number>(employee.branch_id ?? 0);
  const [active, setActive] = useState(employee.is_active);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const roles = assignableRoles(me.role);
  // Если текущая роль не из списка доступных (например, Owner для HR Admin) — показываем её, но без выбора.
  const roleOptions = roles.includes(employee.role) ? roles : [employee.role, ...roles];
  const changed = role !== employee.role || branchId !== (employee.branch_id ?? 0) || active !== employee.is_active;

  async function save() {
    setBusy(true);
    setError(null);
    try {
      const updated = await api.updateEmployee(employee.id, {
        ...(role !== employee.role && { role }),
        ...(branchId !== (employee.branch_id ?? 0) && { branch_id: branchId }),
        ...(active !== employee.is_active && { is_active: active }),
      });
      haptic("success");
      onDone(updated);
    } catch (e: unknown) {
      haptic("error");
      setError(errorText(e, "Не удалось сохранить изменения"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="stack">
      <h1>{employee.full_name || `ID ${employee.telegram_id}`}</h1>

      <label>
        Роль
        <select value={role} onChange={(e) => setRole(e.target.value)}>
          {roleOptions.map((r) => (
            <option key={r} value={r} disabled={!roles.includes(r)}>{ROLE_LABELS[r] ?? r}</option>
          ))}
        </select>
      </label>

      <label>
        Филиал
        <select value={branchId} onChange={(e) => setBranchId(Number(e.target.value))}>
          <option value={0}>Без филиала</option>
          {branches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
        </select>
      </label>

      <label className="check">
        <input type="checkbox" checked={active} onChange={(e) => setActive(e.target.checked)} />
        Доступ открыт
      </label>

      <p className="muted small">После сохранения сотрудник выйдет из системы и при следующем входе получит новые права.</p>
      {error && <p className="error">{error}</p>}

      <button className="btn" disabled={busy || !changed} onClick={save}>{busy ? "Сохранение…" : "Сохранить"}</button>
      <button className="btn ghost" onClick={onCancel}>Отмена</button>
    </section>
  );
}
