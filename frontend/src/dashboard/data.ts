// Демо-данные для макета. Позже заменяются запросами к API.
export const NAV = ["Главная", "Кандидаты", "Сообщения", "Расписание", "Отчёты", "Помощь"] as const;

export const STATS = [
  { label: "Всего кандидатов", value: 1508, note: "за 3 месяца", pct: 75, color: "#f97316" },
  { label: "Приглашены на интервью", value: 1425, note: "за 6 месяцев", pct: 65, color: "#3b82f6" },
  { label: "Опубликовано вакансий", value: 1135, note: "за 8 месяцев", pct: 65, color: "#22c55e" },
];

export const TOP = [
  { place: "1-е", name: "Роберт Джонсон", email: "robert@example.com", points: 623, color: "#b45309" },
  { place: "2-е", name: "Джеймс Родригес", email: "james@example.com", points: 623, color: "#3b5bdb" },
  { place: "3-е", name: "Дэвид Гарсия", email: "david@example.com", points: 623, color: "#2f9e44" },
];

export type InterviewStatus = "Не завершено" | "Завершено" | "В процессе";
export const INTERVIEWS: { name: string; post: string; role: string; time: string; status: InterviewStatus }[] = [
  { name: "Ричард Томпсон", post: "Разработчик", role: "Бэкенд", time: "11:30", status: "Не завершено" },
  { name: "София Эрнандес", post: "Дизайнер", role: "UI/UX", time: "12:30", status: "Завершено" },
  { name: "София Эрнандес", post: "Копирайтер", role: "Контент", time: "11:30", status: "В процессе" },
];

export const JOBS = [
  { title: "UI/UX дизайнер", company: "Globe Corporation", tags: ["Удалённо", "Полный день"] },
  { title: "Веб-разработчик", company: "Stating Cooper", tags: ["Полный день", "Удалённо"] },
  { title: "Графический дизайнер", company: "Soylent Corp", tags: ["Полный день", "Удалённо"] },
];

export const PRESENCE = [
  { day: "Сб", v: 52 }, { day: "Вс", v: 37 }, { day: "Пн", v: 72 }, { day: "Вт", v: 52 }, { day: "Ср", v: 37 },
];

export const INSTRUCTORS = ["ИА", "МК", "ОС", "ДП", "ЕВ"];
