import { useEffect, useState } from "react";
import { api, clearToken } from "./api";
import type { Me } from "./types";
import Candidates from "./components/Candidates";
import Vacancies from "./components/Vacancies";

type State = { s: "loading" } | { s: "error"; msg: string } | { s: "ready"; me: Me };
type Tab = "candidates" | "vacancies";

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
        <button className={tab === "candidates" ? "on" : ""} onClick={() => setTab("candidates")}>Кандидаты</button>
        <button className={tab === "vacancies" ? "on" : ""} onClick={() => setTab("vacancies")}>Вакансии</button>
      </nav>
      {tab === "candidates" ? <Candidates me={me} /> : <Vacancies me={me} />}
    </div>
  );
}
