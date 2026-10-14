"""Уведомления сотрудникам отправляет API (app.services.notifications) через Bot API.

Бот-процесс здесь ничего не обрабатывает: роутер оставлен, чтобы подключение в bot/main.py не менялось.
"""
from aiogram import Router

router = Router()
