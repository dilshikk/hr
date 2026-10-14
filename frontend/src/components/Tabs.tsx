export type Tab = "candidates" | "interviews" | "vacancies" | "employees" | "branches";

const TABS: { id: Tab; label: string }[] = [
  { id: "candidates", label: "Кандидаты" },
  { id: "interviews", label: "Интервью" },
  { id: "vacancies", label: "Вакансии" },
  { id: "employees", label: "Сотрудники" },
  { id: "branches", label: "Филиалы" },
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
