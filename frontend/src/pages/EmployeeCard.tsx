import { useState } from "react";
import { api, errorText } from "../api";
import { haptic } from "../telegram";
import { canEditEmployee, canResetTwoFactor, ROLE_LABELS, type Employee, type Me } from "../types";

type Props = {
  me: Me;
  employee: Employee;
  branchName: string;
  onEdit: () => void;
  onBack: () => void;
};

/** Карточка сотрудника: просмотр для всех, кнопка «Изменить» — только если роль позволяет (сервер проверяет сам). */
export default function EmployeeCard({ me, employee, branchName, onEdit, onBack }: Props) {
  const editable = canEditEmployee(me, employee);
  const resettable = canResetTwoFactor(me, employee);
  const title = employee.full_name || `ID ${employee.telegram_id}`;
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  async function reset() {
    setBusy(true);
    setError(null);
    try {
      await api.resetEmployeeTwoFactor(employee.id);
      haptic("success");
      setDone(true);
      setConfirming(false);
    } catch (e: unknown) {
      haptic("error");
      setError(errorText(e, "Не удалось сбросить 2FA"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section>
      <h1>{title}{employee.id === me.id && " (вы)"}</h1>
      {employee.is_active ? (
        <span className="badge stage-hired">Доступ открыт</span>
      ) : (
        <span className="badge stage-rejected">Заблокирован</span>
      )}

      <dl className="details">
        <dt>Роль</dt>
        <dd>{ROLE_LABELS[employee.role] ?? employee.role}</dd>
        <dt>Филиал</dt>
        <dd>{branchName}</dd>
        <dt>Telegram ID</dt>
        <dd>{employee.telegram_id}</dd>
        <dt>Номер в системе</dt>
        <dd>{employee.id}</dd>
      </dl>

      {!editable && (
        <p className="muted small">
          {employee.id === me.id
            ? "Свои права менять нельзя."
            : "Ваша роль не позволяет менять этого сотрудника."}
        </p>
      )}

      {done && <p className="muted">2FA сброшена. При следующем входе сотрудник настроит её заново.</p>}
      {error && <p className="error">{error}</p>}

      {confirming && (
        <div className="stack">
          <p className="muted small">
            Сотрудник выйдет из системы, а старые коды перестанут работать. Сбрасывайте только если уверены, что это именно он.
          </p>
          <button className="btn danger" disabled={busy} onClick={reset}>
            {busy ? "Сброс…" : "Да, сбросить 2FA"}
          </button>
          <button className="btn ghost" disabled={busy} onClick={() => setConfirming(false)}>Отмена</button>
        </div>
      )}

      {!confirming && (
        <div className="stack">
          {editable && <button className="btn" onClick={onEdit}>Изменить</button>}
          {resettable && (
            <button className="btn ghost" onClick={() => setConfirming(true)}>Сбросить 2FA</button>
          )}
          <button className="btn ghost" onClick={onBack}>К списку</button>
        </div>
      )}
    </section>
  );
}
