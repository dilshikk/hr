export type Stage =
  | "new" | "review" | "contact" | "interview" | "trial"
  | "offer" | "hired" | "rejected" | "reserve";

export type Candidate = {
  id: number;
  full_name: string;
  phone: string | null;
  branch_id: number;
  vacancy_id: number | null;
  stage: Stage;
};

export type Vacancy = { id: number; title: string; branch_id: number; status: string };
export type Branch = { id: number; name: string };
export type Me = { id: number; name: string; role: string; branch_id: number | null };

export const STAGE_LABELS: Record<Stage, string> = {
  new: "Новый",
  review: "Рассмотрение",
  contact: "Связались",
  interview: "Собеседование",
  trial: "Стажировка",
  offer: "Оффер",
  hired: "Принят",
  rejected: "Отказ",
  reserve: "Резерв",
};

// Должно совпадать с backend/app/services/pipeline.py; сервер всё равно проверяет переход сам.
export const TRANSITIONS: Record<Stage, Stage[]> = {
  new: ["review", "rejected", "reserve"],
  review: ["contact", "rejected", "reserve"],
  contact: ["interview", "rejected", "reserve"],
  interview: ["trial", "offer", "rejected", "reserve"],
  trial: ["offer", "rejected", "reserve"],
  offer: ["hired", "rejected", "reserve"],
  reserve: ["review", "contact", "rejected"],
  hired: [],
  rejected: [],
};

const WRITE_ROLES = new Set(["owner", "hr_admin", "recruiter", "branch_manager"]);
export const canWrite = (role: string) => WRITE_ROLES.has(role);
