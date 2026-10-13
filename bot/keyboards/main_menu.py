from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo


def webapp_keyboard(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Открыть HR-панель", web_app=WebAppInfo(url=url)),
    ]])
