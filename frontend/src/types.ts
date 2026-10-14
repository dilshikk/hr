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
export type Employee = {
  id: number;
  telegram_id: number;
  full_name: string;
  role: string;
  branch_id: number | null;
  is_active: boolean;
};

export type InterviewListItem = {
  id: number;
  user_id: number;
  name: string;
  status: string;
  q_count: number;
};

export type Interview = InterviewListItem & {
  qa_log: { q: string; a: string }[];
  report_resume: unknown;
  report_skills: unknown;
  report_personality: unknown;
};

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

export const ROLE_LABELS: Record<string, string> = {
  owner: "Владелец",
  hr_admin: "HR-администратор",
  recruiter: "Рекрутер",
  branch_manager: "Управляющий филиалом",
  viewer: "Только просмотр",
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
// Права ниже совпадают с backend/app/core/permissions.py (сервер проверяет сам, здесь только для показа UI).
export const isManager = (role: string) => role === "owner" || role === "hr_admin";
export const isOwner = (role: string) => role === "owner";

/** Какие роли текущий пользователь может выдавать (HR Admin не выдаёт Owner/HR Admin). */
export function assignableRoles(actorRole: string): string[] {
  if (actorRole === "owner") return Object.keys(ROLE_LABELS);
  if (actorRole === "hr_admin") return ["recruiter", "branch_manager", "viewer"];
  return [];
}

/** Может ли текущий пользователь менять этого сотрудника. */
export function canEditEmployee(me: Me, target: Employee): boolean {
  if (me.id === target.id) return false;
  if (me.role === "owner") return true;
  return me.role === "hr_admin" && !isManager(target.role);
}

/** Сброс 2FA: только Owner, только другому сотруднику с обязательной 2FA (как can_reset_2fa на сервере). */
export function canResetTwoFactor(me: Me, target: Employee): boolean {
  return isOwner(me.role) && me.id !== target.id && isManager(target.role);
}
