import { useEffect, useState } from "react";
import { api, clearToken } from "../services/api";
import type { Me } from "../types";
import Candidates from "../pages/Candidates/Candidates";
import Vacancies from "../pages/Vacancies/Vacancies";
import Interviews from "../pages/Interviews/Interviews";

type State = { s: "loading" } | { s: "error"; msg: string } | { s: "ready"; me: Me };
type Tab = "candidates" | "vacancies" | "interviews";

const TABS: { id: Tab; label: string }[] = [
  { id: "candidates", label: "Кандидаты" },
  { id: "vacancies", label: "Вакансии" },
  { id: "interviews", label: "Интервью" },
];

export default function App() {
  const [state, setState] = useState<State>({ s: "loading" });
  const [tab, setTab] = useState<Tab>("candidates");

  useEffect(() => {
    const init = async () => {
      const initData = window.Telegram?.WebApp.initData ?? "";
      if (!initData) {
        setState({ s: "error", msg: "Откройте панель через кнопку в Telegram-боте." });
        return;
      }
      try {
        await api.login(initData);
        setState({ s: "ready", me: await api.get<Me>("/me") });
      } catch (e) {
        clearToken();
        setState({ s: "error", msg: e instanceof Error ? e.message : "Не удалось войти" });
      }
    };
    void init();
  }, []);

  if (state.s === "loading") return <p className="center">Загрузка...</p>;
  if (state.s === "error") return <p className="center error">{state.msg}</p>;

  const { me } = state;
  return (
    <div className="app">
      <header>
        <b>MADO HR</b>
        <span className="muted">{me.name} · {me.role}</span>
      </header>
      <nav>
        {TABS.map((t) => (
          <button key={t.id} className={tab === t.id ? "on" : ""} onClick={() => setTab(t.id)}>{t.label}</button>
        ))}
      </nav>
      {tab === "candidates" && <Candidates me={me} />}
      {tab === "vacancies" && <Vacancies me={me} />}
      {tab === "interviews" && <Interviews />}
    </div>
  );
}
