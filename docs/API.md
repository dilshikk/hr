# API v1

Базовый путь: `/api/v1`. Авторизация: заголовок `Authorization: Bearer <token>`. Swagger отключён в продакшене.

## Авторизация
| Метод | Путь | Описание |
|---|---|---|
| POST | `/auth/telegram` | Тело `{init_data}` из Telegram WebApp. Возвращает `{token, role}` |
| POST | `/auth/logout` | Отзывает текущую сессию |
| GET | `/me` | Текущий пользователь: id, имя, роль, филиал |

## Кандидаты
| Метод | Путь | Право | Описание |
|---|---|---|---|
| GET | `/candidates?stage=&limit=&offset=` | read | Список (только свой филиал, кроме Owner/HR Admin) |
| POST | `/candidates` | write_candidates | Создать: `full_name, phone?, branch_id, vacancy_id?` |
| GET | `/candidates/{id}` | read | Карточка; чужой филиал → 404 |
| POST | `/candidates/{id}/stage` | write_candidates | `{stage, reason}`; недопустимый переход → 400 |

## Вакансии
| Метод | Путь | Право | Описание |
|---|---|---|---|
| GET | `/vacancies` | read | Список по филиалу |
| POST | `/vacancies` | write_vacancies | Создать: `title, branch_id, description?` |

## Заготовки (без эндпоинтов)
`/interviews`, `/employees`, `/branches`, `/admin`, `/reports`.

## Служебное
`GET /health/live` → `{status: "ok"}`.

## Коды ошибок
401 — нет/недействительная сессия; 403 — нет прав или доступ закрыт; 404 — не найдено (в т.ч. чужой филиал); 400 — неверные данные.
