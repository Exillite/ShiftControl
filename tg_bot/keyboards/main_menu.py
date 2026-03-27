from unittest import result

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

from services.api import api

async def main_menu(user):
    inline_keyboard = []
    if user.username == os.getenv("ROOT_ADMIN_USERNAME"):
        inline_keyboard.append([InlineKeyboardButton(text="📂 Группы", callback_data="menu:groups")])
        inline_keyboard.append([InlineKeyboardButton(text="👥 Сотрудники", callback_data="menu:employees")])
        inline_keyboard.append([InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu:settings")])


    result = await api.is_user_admin(user.id)

    is_admin = False
    if result and result.get("status") == "ok":
        is_admin = result["data"]["is_admin"]
    
    if is_admin or user.username == os.getenv("ROOT_ADMIN_USERNAME"):
        inline_keyboard.append([InlineKeyboardButton(text="Ручная проверка", callback_data="menu:checks")])

    return InlineKeyboardMarkup(
        inline_keyboard=inline_keyboard
    )