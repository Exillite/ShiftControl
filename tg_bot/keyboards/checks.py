from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def check_kb(shift_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Подтвердить",
                callback_data=f"shift_ok:{shift_id}"
            ),
            InlineKeyboardButton(
                text="❌ Отклонить",
                callback_data=f"shift_no:{shift_id}"
            ),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
        ]
    ])