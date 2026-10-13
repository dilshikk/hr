# REST API (/api/v1)

Заголовок: `Authorization: Bearer <token>`. Ошибки: `{"detail": "текст"}`.

| Метод | Путь | Права | Описание |
|---|---|---|---|
| POST | /auth/telegram | — | Вход по initData, возвращает токен и роль |
| POST | /auth/logout | вход | Отзыв сессии |
| GET | /me | вход | Текущий пользователь |
| GET | /branches | read | Доступные филиалы |
| POST | /branches | manage_branches | Создать филиал |
| GET | /candidates?stage=&limit=&offset= | read | Список (по филиалу пользователя) |
| POST | /candidates | write_candidates | Создать |
| GET | /candidates/{id} | read | Карточка |
| POST | /candidates/{id}/stage | write_candidates | Перевод по воронке, для отказа нужна `reason` |
| GET | /vacancies | read | Список |
| POST | /vacancies | write_vacancies | Создать |
| GET | /interviews, /employees, /admin/audit, /reports | — | Пока 501 (после MVP) |

Служебный адрес: `GET /health/live`.
