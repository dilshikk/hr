import { api } from "../api";
import { useLoad } from "../hooks/useLoad";
import { STAGE_LABELS, type Stage } from "../types";

type Props = { onNewCandidate: () => void };

/** Главная: ключевые показатели найма и воронка по этапам. */
export default function Home({ onNewCandidate }: Props) {
  const summary = useLoad(api.dashboard, "Не удалось загрузить показатели");
  const data = summary.data;

  const cards = data && [
    { label: "Новые за 7 дней", value: data.new_last_week },
    { label: "В работе", value: data.in_progress },
    { label: "Открытые вакансии", value: data.open_vacancies },
    { label: "Принято", value: data.hired },
  ];

  return (
    <section>
      <h1>Главная</h1>

      {summary.error && (
        <div className="stack">
          <p className="error">{summary.error}</p>
          <button className="btn ghost" onClick={summary.reload}>Повторить</button>
        </div>
      )}
      {!summary.error && !data && <p className="muted">Загрузка…</p>}

      {data && cards && (
        <>
          <div className="stats">
            {cards.map((c) => (
              <div key={c.label} className="stat">
                <span className="stat-value">{c.value}</span>
                <span className="muted small">{c.label}</span>
              </div>
            ))}
          </div>

          <button className="btn full" onClick={onNewCandidate}>Новый кандидат</button>

          <h2>Воронка</h2>
          {data.total === 0 ? (
            <p className="muted">Кандидатов пока нет. Добавьте первого, и здесь появится воронка.</p>
          ) : (
            <ul className="list">
              {(Object.keys(STAGE_LABELS) as Stage[]).map((s) => (
                <li key={s} className="item static">
                  <span>{STAGE_LABELS[s]}</span>
                  <span className="badge">{data.by_stage[s]}</span>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </section>
  );
}
