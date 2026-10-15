export type Tab = "home" | "candidates" | "schedule" | "interviews" | "vacancies" | "employees" | "branches" | "audit";

const TABS: { id: Tab; label: string }[] = [
  { id: "home", label: "Главная" },
  { id: "candidates", label: "Кандидаты" },
  { id: "schedule", label: "Календарь" },
  { id: "interviews", label: "Опросы" },
  { id: "vacancies", label: "Вакансии" },
  { id: "employees", label: "Сотрудники" },
  { id: "branches", label: "Филиалы" },
  { id: "audit", label: "Журнал" },
];

type Props = { active: Tab; onChange: (t: Tab) => void };

/** Нижняя панель вкладок. Показывается только руководству (Owner/HR Admin). */
export default function Tabs({ active, onChange }: Props) {
  return (
    <nav className="tabs">
      {TABS.map((t) => (
        <button key={t.id} className={t.id === active ? "tab active" : "tab"} onClick={() => onChange(t.id)}>
          {t.label}
        </button>
      ))}
    </nav>
  );
}
