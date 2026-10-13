import type { Branch, Candidate, Me, Stage, Vacancy } from "./types";

const BASE = "/api/v1";

// Токен только в памяти: не пишем в localStorage, чтобы его нельзя было украсть после закрытия.
let token: string | null = null;

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(BASE + path, { ...init, headers });
  if (!res.ok) {
    let message = "Что-то пошло не так. Попробуйте ещё раз";
    try {
      const body: unknown = await res.json();
      if (body && typeof body === "object" && "detail" in body && typeof body.detail === "string") {
        message = body.detail;
      }
    } catch {
      /* тело не JSON — оставляем общее сообщение */
    }
    throw new ApiError(res.status, message);
  }
  return res.json() as Promise<T>;
}

export async function login(initData: string): Promise<void> {
  const res = await request<{ token: string }>("/auth/telegram", {
    method: "POST",
    body: JSON.stringify({ init_data: initData }),
  });
  token = res.token;
}

export const api = {
  me: () => request<Me>("/me"),
  candidates: (stage: Stage | "") =>
    request<Candidate[]>(`/candidates?limit=100${stage ? `&stage=${stage}` : ""}`),
  candidate: (id: number) => request<Candidate>(`/candidates/${id}`),
  createCandidate: (body: { full_name: string; phone: string | null; branch_id: number; vacancy_id: number | null }) =>
    request<Candidate>("/candidates", { method: "POST", body: JSON.stringify(body) }),
  moveStage: (id: number, stage: Stage, reason: string) =>
    request<Candidate>(`/candidates/${id}/stage`, { method: "POST", body: JSON.stringify({ stage, reason }) }),
  vacancies: () => request<Vacancy[]>("/vacancies?limit=100"),
  branches: () => request<Branch[]>("/branches"),
};
