import { createRoot } from "react-dom/client";
import App from "./App";
import Dashboard from "./dashboard/Dashboard";
import "./styles.css";
import "./dashboard/dashboard.css";

window.Telegram?.WebApp.ready();

// ?demo=1 открывает макет панели с демо-данными, без входа через Telegram.
const isDemo = new URLSearchParams(window.location.search).has("demo");
createRoot(document.getElementById("root")!).render(isDemo ? <Dashboard /> : <App />);
