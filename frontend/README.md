# Telegram Mini App

React + TypeScript + Vite. Рабочее место сотрудника: список кандидатов, карточка, смена этапа, добавление.

```bash
cd frontend
npm install
npm run dev     # локально, /api проксируется на 127.0.0.1:8000
npm run build   # сборка в frontend/dist, раздаётся nginx
```

Открывается только из Telegram (кнопка в боте): вход идёт по initData. Токен сессии хранится только в памяти вкладки.
