from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo


def open_panel_keyboard(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Открыть HR-панель", web_app=WebAppInfo(url=url)),
    ]])
