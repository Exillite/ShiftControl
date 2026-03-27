from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def settings_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить", callback_data="set_time")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])