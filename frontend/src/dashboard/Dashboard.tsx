import { useState } from "react";
import Ring from "./Ring";
import { INSTRUCTORS, INTERVIEWS, JOBS, NAV, PRESENCE, STATS, TOP, type InterviewStatus } from "./data";

const STATUS_CLASS: Record<InterviewStatus, string> = {
  "Не завершено": "st-blue",
  "Завершено": "st-green",
  "В процессе": "st-orange",
};

const initials = (name: string) => name.split(" ").map((p) => p[0]).join("");

export default function Dashboard() {
  const [active, setActive] = useState<string>(NAV[0]);
  const max = Math.max(...PRESENCE.map((p) => p.v));

  return (
    <div className="dash">
      <aside className="side">
        <div className="logo">MADO</div>
        {NAV.map((n) => (
          <button key={n} className={`nav ${active === n ? "on" : ""}`} onClick={() => setActive(n)}>{n}</button>
        ))}
        <div className="me"><span className="ava">ДС</span> Dilshit</div>
      </aside>

      <main className="main">
        <header className="top">
          <h1>Здравствуйте, Дилшит</h1>
          <input className="search" placeholder="Поиск" />
        </header>

        <section className="panel stats">
          {STATS.map((s) => (
            <div className="stat" key={s.label}>
              <div>
                <div className="muted">{s.label}</div>
                <div className="big">{s.value}</div>
                <div className="muted small">{s.note}</div>
              </div>
              <Ring pct={s.pct} color={s.color} />
            </div>
          ))}
        </section>

        <section className="tops">
          {TOP.map((t) => (
            <div className="top-card" style={{ background: t.color }} key={t.name}>
              <span className="place">{t.place}</span>
              <span className="ava big-ava">{initials(t.name)}</span>
              <b>{t.name}</b>
              <span className="small">{t.email}</span>
              <span className="small">Баллов: {t.points}</span>
              <button className="ghost">Подробнее</button>
            </div>
          ))}
        </section>

        <section className="panel">
          <div className="row-between">
            <b>Расписание интервью</b>
            <select className="sel"><option>Сегодня</option><option>Завтра</option></select>
          </div>
          <table>
            <thead><tr><th>Кандидат</th><th>Должность</th><th>Направление</th><th>Время</th><th>Статус</th></tr></thead>
            <tbody>
              {INTERVIEWS.map((i, idx) => (
                <tr key={idx}>
                  <td><span className="ava">{initials(i.name)}</span> {i.name}</td>
                  <td>{i.post}</td><td>{i.role}</td><td>{i.time}</td>
                  <td><span className={`pill ${STATUS_CLASS[i.status]}`}>{i.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </main>

      <aside className="right">
        <div className="row-between"><b>Рекомендуемые вакансии</b><span className="muted small">Все</span></div>
        {JOBS.map((j) => (
          <div className="panel job" key={j.title}>
            <b>{j.title}</b>
            <div className="muted small">{j.company}</div>
            <div className="tags">{j.tags.map((t, i) => <span key={t} className={`tag ${i ? "t-blue" : "t-green"}`}>{t}</span>)}</div>
          </div>
        ))}
        <div className="panel">
          <b>Интервьюеры</b>
          <div className="avas">{INSTRUCTORS.map((a) => <span key={a} className="ava">{a}</span>)}</div>
        </div>
        <div className="panel">
          <b>Посещаемость</b>
          <div className="bars">
            {PRESENCE.map((p) => (
              <div key={p.day} className="bar-col">
                <div className="bar" style={{ height: `${(p.v / max) * 100}px` }} />
                <span className="muted small">{p.day}</span>
              </div>
            ))}
          </div>
        </div>
      </aside>
    </div>
  );
}
