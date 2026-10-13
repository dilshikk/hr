import { useEffect, useState } from "react";
import { api, errorText, login } from "./api";
import { tg } from "./telegram";
import { isManager, type Me } from "./types";
import Tabs, { type Tab } from "./components/Tabs";
import CandidateList from "./pages/CandidateList";
import CandidateCard from "./pages/CandidateCard";
import CandidateForm from "./pages/CandidateForm";
import VacancyList from "./pages/VacancyList";
import EmployeeList from "./pages/EmployeeList";
import BranchList from "./pages/BranchList";

type Screen = { name: "list" } | { name: "card"; id: number } | { name: "new" };
type AuthState = { status: "loading" } | { status: "error"; message: string } | { status: "ok"; me: Me };

export default function App() {
  const [auth, setAuth] = useState<AuthState>({ status: "loading" });
  const [tab, setTab] = useState<Tab>("candidates");
  const [screen, setScreen] = useState<Screen>({ name: "list" });

  // Вход один раз при открытии Mini App.
  useEffect(() => {
    tg?.ready();
    tg?.expand();
    if (!tg?.initData) {
      setAuth({ status: "error", message: "Откройте панель из Telegram-бота MADO" });
      return;
    }
    login(tg.initData)
      .then(api.me)
      .then((me) => setAuth({ status: "ok", me }))
      .catch((e: unknown) => setAuth({ status: "error", message: errorText(e, "Не удалось войти") }));
  }, []);

  // Системная кнопка «Назад» Telegram на вложенных экранах кандидатов.
  useEffect(() => {
    const back = tg?.BackButton;
    if (!back) return;
    if (tab !== "candidates" || screen.name === "list") {
      back.hide();
      return;
    }
    const goBack = () => setScreen({ name: "list" });
    back.show();
    back.onClick(goBack);
    return () => back.offClick(goBack);
  }, [screen, tab]);

  if (auth.status === "loading") return <div className="center muted">Вход…</div>;
  if (auth.status === "error") return <div className="center error">{auth.message}</div>;

  const { me } = auth;
  const manager = isManager(me.role);
  const toList = () => setScreen({ name: "list" });

  return (
    <>
      <main className={manager ? "app with-tabs" : "app"}>
        {tab === "candidates" && (
          <>
            {screen.name === "list" && (
              <CandidateList me={me} onOpen={(id) => setScreen({ name: "card", id })} onNew={() => setScreen({ name: "new" })} />
            )}
            {screen.name === "card" && <CandidateCard id={screen.id} me={me} onBack={toList} />}
            {screen.name === "new" && (
              <CandidateForm me={me} onDone={(id) => setScreen({ name: "card", id })} onCancel={toList} />
            )}
          </>
        )}
        {manager && tab === "vacancies" && <VacancyList />}
        {manager && tab === "employees" && <EmployeeList me={me} />}
        {manager && tab === "branches" && <BranchList me={me} />}
      </main>
      {manager && (
        <Tabs
          active={tab}
          onChange={(t) => {
            setTab(t);
            setScreen({ name: "list" });
          }}
        />
      )}
    </>
  );
}
