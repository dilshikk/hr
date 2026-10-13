# Mini App (frontend)

React + Vite + TypeScript. Работает только внутри Telegram: вход по `initData`.

```
cd frontend
npm install
npm run dev      # прокси /api на localhost:8000
npm run build    # результат в frontend/dist
```

Собранную папку `dist` нужно раздавать по HTTPS на домене из `WEBAPP_URL`.
Этот же домен укажите в `ALLOWED_ORIGINS`, если API находится на другом адресе.
Номер филиала вводится вручную: списка филиалов в API пока нет.
