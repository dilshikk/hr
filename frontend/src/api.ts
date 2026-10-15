import type { Branch, Candidate, Employee, Interview, InterviewListItem, Me, Stage, Vacancy } from "./types";

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

type SessionResponse = {
  token: string | null;
  role: string;
  twofa: "setup" | "verify" | null;
  challenge: string | null;
  recovery_codes: string[] | null;
};

/** Первый шаг входа. Owner и HR Admin получают не сессию, а задание «введите код». */
export type LoginResult =
  | { status: "ok" }
  | { status: "twofa"; mode: "setup" | "verify"; challenge: string };

export async function login(initData: string): Promise<LoginResult> {
  const res = await request<SessionResponse>("/auth/telegram", {
    method: "POST",
    body: JSON.stringify({ init_data: initData }),
  });
  if (res.twofa && res.challenge) return { status: "twofa", mode: res.twofa, challenge: res.challenge };
  token = res.token;
  return { status: "ok" };
}

const post = (body: unknown): RequestInit => ({ method: "POST", body: JSON.stringify(body) });

export const twofa = {
  setup: (challenge: string) => request<{ secret: string; uri: string }>("/auth/2fa/setup", post({ challenge })),
  /** Подтверждает первый код; возвращает коды восстановления (показываются один раз). */
  async confirm(challenge: string, code: string): Promise<string[]> {
    const res = await request<SessionResponse>("/auth/2fa/confirm", post({ challenge, code }));
    token = res.token;
    return res.recovery_codes ?? [];
  },
  async verify(challenge: string, code: string): Promise<void> {
    const res = await request<SessionResponse>("/auth/2fa/verify", post({ challenge, code }));
    token = res.token;
  },
};

export type Dashboard = {
  total: number;
  new_last_week: number;
  in_progress: number;
  hired: number;
  open_vacancies: number;
  by_stage: Record<Stage, number>;
};

export type AuditEntry = {
  id: number;
  actor_id: number | null;
  actor_name: string | null;
  action: string;
  target: string;
  created_at: string;
};

export type ScheduleStatus = "scheduled" | "done" | "cancelled";

export type ScheduledInterview = {
  id: number;
  candidate_id: number;
  candidate_name: string;
  interviewer_id: number;
  interviewer_name: string;
  starts_at: string;
  duration_min: number;
  format: "offline" | "online";
  status: ScheduleStatus;
  score: number | null;
  comment: string;
};

export type NewScheduledInterview = {
  candidate_id: number;
  interviewer_id: number;
  starts_at: string;
  duration_min: number;
  format: "offline" | "online";
};

export const api = {
  me: () => request<Me>("/me"),
  dashboard: () => request<Dashboard>("/dashboard/summary"),
  audit: (action: string, offset: number, limit: number) =>
    request<AuditEntry[]>(
      `/audit?limit=${limit}&offset=${offset}${action ? `&action=${encodeURIComponent(action)}` : ""}`,
    ),
  schedule: (status: ScheduleStatus) => request<ScheduledInterview[]>(`/schedule?limit=100&status=${status}`),
  createInterview: (body: NewScheduledInterview) => request<ScheduledInterview>("/schedule", post(body)),
  cancelInterview: (id: number) => request<ScheduledInterview>(`/schedule/${id}/cancel`, { method: "POST" }),
  scoreInterview: (id: number, score: number, comment: string) =>
    request<ScheduledInterview>(`/schedule/${id}/score`, post({ score, comment })),
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
  resetEmployeeTwoFactor: (id: number) => request<Employee>(`/employees/${id}/reset-2fa`, { method: "POST" }),
  interviews: () => request<InterviewListItem[]>("/interviews?limit=100"),
  interview: (id: number) => request<Interview>(`/interviews/${id}`),
};
