import { createRoot } from "react-dom/client";
import App from "./app/App";
import Home from "./pages/Home/Home";
import "./styles.css";
import "./features/dashboard/dashboard.css";

window.Telegram?.WebApp.ready();

// ?demo=1 открывает макет панели с демо-данными, без входа через Telegram.
const isDemo = new URLSearchParams(window.location.search).has("demo");
createRoot(document.getElementById("root")!).render(isDemo ? <Home /> : <App />);
