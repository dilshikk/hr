# API v1

Базовый путь: `/api/v1`. Авторизация: заголовок `Authorization: Bearer <token>`. Swagger отключён в продакшене.

## Авторизация
| Метод | Путь | Описание |
|---|---|---|
| POST | `/auth/telegram` | Тело `{init_data}` из Telegram WebApp. Возвращает `{token, role}`. Не более 10 попыток в минуту с IP (429) |
| POST | `/auth/logout` | Отзывает текущую сессию |
| GET | `/me` | Текущий пользователь: id, имя, роль, филиал |

## Кандидаты
| Метод | Путь | Право | Описание |
|---|---|---|---|
| GET | `/candidates?stage=&limit=&offset=` | read | Список (только свой филиал, кроме Owner/HR Admin) |
| POST | `/candidates` | write_candidates | Создать: `full_name, phone?, branch_id, vacancy_id?`; вакансия из другого филиала → 400 |
| GET | `/candidates/{id}` | read | Карточка; чужой филиал → 404 |
| POST | `/candidates/{id}/stage` | write_candidates | `{stage, reason}`; недопустимый переход → 400; этап уже изменён другим → 409 |

## Вакансии
| Метод | Путь | Право | Описание |
|---|---|---|---|
| GET | `/vacancies` | read | Список по филиалу |
| POST | `/vacancies` | write_vacancies | Создать: `title, branch_id, description?` |

## Сотрудники
| Метод | Путь | Право | Описание |
|---|---|---|---|
| GET | `/employees?limit=&offset=` | manage_users | Список сотрудников |
| PATCH | `/employees/{id}` | manage_users | `{role?, branch_id?, is_active?}`; `branch_id: 0` — снять филиал |

Правила: себя менять нельзя; HR Admin не может трогать Owner/HR Admin и назначать эти роли; Owner — без ограничений. После изменения все сессии сотрудника отзываются.

## Филиалы
| Метод | Путь | Право | Описание |
|---|---|---|---|
| GET | `/branches` | read | Список филиалов |
| POST | `/branches` | manage_branches (только Owner) | `{name}`; дубликат → 409 |

## Заготовки (без эндпоинтов)
`/interviews`, `/admin`, `/reports`.

## Служебное
`GET /health/live` → `{status: "ok"}`.

## Коды ошибок
401 — нет/недействительная сессия; 403 — нет прав или доступ закрыт; 404 — не найдено (в т.ч. чужой филиал); 400 — неверные данные; 409 — конфликт; 429 — слишком много попыток.
