import { useCallback, useEffect, useState } from "react";
import { api, errorText, login } from "./api";
import { tg } from "./telegram";
import { isManager, type Me } from "./types";
import Tabs, { type Tab } from "./components/Tabs";
import Home from "./pages/Home";
import CandidateList from "./pages/CandidateList";
import CandidateCard from "./pages/CandidateCard";
import CandidateForm from "./pages/CandidateForm";
import Schedule from "./pages/Schedule";
import VacancyList from "./pages/VacancyList";
import EmployeeList from "./pages/EmployeeList";
import BranchList from "./pages/BranchList";
import InterviewList from "./pages/InterviewList";
import AuditLog from "./pages/AuditLog";
import TwoFactor from "./pages/TwoFactor";

type Screen = { name: "list" } | { name: "card"; id: number } | { name: "new" };
type AuthState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "twofa"; mode: "setup" | "verify"; challenge: string }
  | { status: "ok"; me: Me };

export default function App() {
  const [auth, setAuth] = useState<AuthState>({ status: "loading" });
  const [tab, setTab] = useState<Tab>("candidates");
  const [screen, setScreen] = useState<Screen>({ name: "list" });

  // После получения сессии (сразу или после 2FA) загружаем профиль.
  // Руководство начинает с главной, остальные роли - со списка кандидатов (вкладок у них нет).
  const loadMe = useCallback(() => {
    api.me()
      .then((me) => {
        if (isManager(me.role)) setTab("home");
        setAuth({ status: "ok", me });
      })
      .catch((e: unknown) => setAuth({ status: "error", message: errorText(e, "Не удалось войти") }));
  }, []);

  // Вход один раз при открытии Mini App.
  useEffect(() => {
    tg?.ready();
    tg?.expand();
    if (!tg?.initData) {
      setAuth({ status: "error", message: "Откройте панель из Telegram-бота MADO" });
      return;
    }
    login(tg.initData)
      .then((result) => {
        if (result.status === "twofa") setAuth(result);
        else loadMe();
      })
      .catch((e: unknown) => setAuth({ status: "error", message: errorText(e, "Не удалось войти") }));
  }, [loadMe]);

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
  if (auth.status === "twofa") {
    return <TwoFactor mode={auth.mode} challenge={auth.challenge} onDone={loadMe} />;
  }

  const { me } = auth;
  const manager = isManager(me.role);
  const toList = () => setScreen({ name: "list" });

  return (
    <>
      <main className={manager ? "app with-tabs" : "app"}>
        {manager && tab === "home" && (
          <Home
            onNewCandidate={() => {
              setTab("candidates");
              setScreen({ name: "new" });
            }}
          />
        )}
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
        {manager && tab === "schedule" && <Schedule />}
        {manager && tab === "interviews" && <InterviewList />}
        {manager && tab === "vacancies" && <VacancyList />}
        {manager && tab === "employees" && <EmployeeList me={me} />}
        {manager && tab === "branches" && <BranchList me={me} />}
        {manager && tab === "audit" && <AuditLog />}
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
