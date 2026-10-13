import type { Branch, Candidate, Employee, Me, Stage, Vacancy } from "./types";

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

export const errorText = (e: unknown, fallback: string) => (e instanceof ApiError ? e.message : fallback);

export async function login(initData: string): Promise<void> {
  const res = await request<{ token: string }>("/auth/telegram", {
    method: "POST",
    body: JSON.stringify({ init_data: initData }),
  });
  token = res.token;
}

const post = (body: unknown): RequestInit => ({ method: "POST", body: JSON.stringify(body) });

export const api = {
  me: () => request<Me>("/me"),
  candidates: (stage: Stage | "") =>
    request<Candidate[]>(`/candidates?limit=100${stage ? `&stage=${stage}` : ""}`),
  candidate: (id: number) => request<Candidate>(`/candidates/${id}`),
  createCandidate: (body: { full_name: string; phone: string | null; branch_id: number; vacancy_id: number | null }) =>
    request<Candidate>("/candidates", post(body)),
  moveStage: (id: number, stage: Stage, reason: string) =>
    request<Candidate>(`/candidates/${id}/stage`, post({ stage, reason })),
  vacancies: () => request<Vacancy[]>("/vacancies?limit=100"),
  createVacancy: (body: { title: string; branch_id: number; description: string }) =>
    request<Vacancy>("/vacancies", post(body)),
  setVacancyStatus: (id: number, status: string) => request<Vacancy>(`/vacancies/${id}/status`, post({ status })),
  branches: () => request<Branch[]>("/branches"),
  createBranch: (name: string) => request<Branch>("/branches", post({ name })),
  employees: () => request<Employee[]>("/employees?limit=100"),
  updateEmployee: (id: number, body: { role?: string; branch_id?: number; is_active?: boolean }) =>
    request<Employee>(`/employees/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
};
