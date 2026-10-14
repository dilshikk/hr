import { canEditEmployee, ROLE_LABELS, type Employee, type Me } from "../types";

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
  const title = employee.full_name || `ID ${employee.telegram_id}`;

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

      <div className="stack">
        {editable && <button className="btn" onClick={onEdit}>Изменить</button>}
        <button className="btn ghost" onClick={onBack}>К списку</button>
      </div>
    </section>
  );
}
