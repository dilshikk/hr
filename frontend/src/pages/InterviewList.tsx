import { useState } from "react";
import { api, errorText } from "../api";
import { useLoad } from "../hooks/useLoad";
import type { Interview } from "../types";

const STATUS_LABELS: Record<string, string> = { active: "Идёт", done: "Завершено" };

/** Отчёт может быть объектом, строкой или пустым значением: показываем как есть, без догадок о формате. */
function ReportBlock({ title, value }: { title: string; value: unknown }) {
  if (value === null || value === undefined) return null;
  const text = typeof value === "string" ? value : JSON.stringify(value, null, 2);
  return (
    <div className="stack">
      <h2>{title}</h2>
      <pre className="small" style={{ whiteSpace: "pre-wrap" }}>{text}</pre>
    </div>
  );
}

function InterviewCard({ id, onBack }: { id: number; onBack: () => void }) {
  const [data, setData] = useState<Interview | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [requested, setRequested] = useState(false);

  // Загружаем один раз при первом показе карточки.
  if (!requested) {
    setRequested(true);
    api.interview(id).then(setData).catch((e: unknown) => setError(errorText(e, "Не удалось загрузить интервью")));
  }

  return (
    <section>
      <button className="btn ghost" onClick={onBack}>К списку</button>
      {error && <p className="error">{error}</p>}
      {!error && !data && <p className="muted">Загрузка…</p>}
      {data && (
        <>
          <h1>{data.name}</h1>
          <span className="badge">{STATUS_LABELS[data.status] ?? data.status}</span>
          {data.qa_log.length === 0 && <p className="muted">Ответов пока нет</p>}
          {data.qa_log.map((item, i) => (
            <div key={i} className="stack">
              <p className="muted small">{item.q}</p>
              <p>{item.a}</p>
            </div>
          ))}
          <ReportBlock title="Резюме" value={data.report_resume} />
          <ReportBlock title="Навыки" value={data.report_skills} />
          <ReportBlock title="Личные качества" value={data.report_personality} />
        </>
      )}
    </section>
  );
}

export default function InterviewList() {
  const list = useLoad(api.interviews, "Не удалось загрузить интервью");
  const [openId, setOpenId] = useState<number | null>(null);

  if (openId !== null) return <InterviewCard id={openId} onBack={() => setOpenId(null)} />;

  return (
    <section>
      <h1>Интервью</h1>
      <p className="muted small">Кандидаты проходят интервью в боте командой /interview</p>
      {list.error && <p className="error">{list.error}</p>}
      {!list.error && list.data === null && <p className="muted">Загрузка…</p>}
      {list.data?.length === 0 && <p className="muted center-text">Интервью пока нет</p>}
      <ul className="list">
        {list.data?.map((i) => (
          <li key={i.id} className="item" onClick={() => setOpenId(i.id)}>
            <span className="item-name">{i.name}</span>
            <span className="muted small">{STATUS_LABELS[i.status] ?? i.status}, ответов: {i.q_count}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
