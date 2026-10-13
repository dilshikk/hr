// Токен хранится только в памяти вкладки (sessionStorage), не в localStorage.
const KEY = "mado_token";

export const getToken = () => sessionStorage.getItem(KEY);
export const clearToken = () => sessionStorage.removeItem(KEY);

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken();
  const res = await fetch(`/api/v1${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(typeof body.detail === "string" ? body.detail : "Ошибка запроса");
  }
  return res.json() as Promise<T>;
}

export const api = {
  get: <T,>(path: string) => request<T>(path),
  post: <T,>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
  async login(initData: string) {
    const out = await request<{ token: string; role: string }>("/auth/telegram", {
      method: "POST",
      body: JSON.stringify({ init_data: initData }),
    });
    sessionStorage.setItem(KEY, out.token);
  },
  async logout() {
    await request("/auth/logout", { method: "POST" }).catch(() => undefined);
    clearToken();
  },
};
