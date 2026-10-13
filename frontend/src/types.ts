export type Me = { id: number; name: string; role: string; branch_id: number | null };
export type Candidate = {
  id: number;
  full_name: string;
  phone: string | null;
  branch_id: number;
  vacancy_id: number | null;
  stage: string;
};
export type Vacancy = { id: number; title: string; branch_id: number; status: string };

declare global {
  interface Window {
    Telegram?: { WebApp: { initData: string; ready: () => void } };
  }
}

export const STAGES: Record<string, string> = {
  new: "Новый",
  review: "Рассмотрение",
  contact: "Контакт",
  interview: "Интервью",
  trial: "Стажировка",
  offer: "Оффер",
  hired: "Принят",
  rejected: "Отказ",
  reserve: "Резерв",
};

// Зеркало правил сервера (domain/pipeline.py). Сервер проверяет всё заново.
export const NEXT: Record<string, string[]> = {
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

export const CAN_WRITE = ["owner", "hr_admin", "recruiter", "branch_manager"];
export const CAN_WRITE_VACANCIES = ["owner", "hr_admin"];
