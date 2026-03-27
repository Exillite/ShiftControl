from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def groups_keyboard(groups: list, bot_username: str):
    kb = []

    for g in groups:
        title = g.get("title") or f"Группа {g['tg_chat_id']}"

        kb.append([
            InlineKeyboardButton(
                text=title,
                callback_data=f"group:{g['id']}"
            )
        ])

    # ➕ добавить бота в группу
    kb.append([
        InlineKeyboardButton(
            text="➕ Добавить бота в группу",
            url=f"https://t.me/{bot_username}?startgroup=true"
        )
    ])

    # назад
    kb.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
    ])

    return InlineKeyboardMarkup(inline_keyboard=kb)