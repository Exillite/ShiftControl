from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def objects_kb(objects: list, group_id: int):
    kb = []

    for obj in objects:
        kb.append([
            InlineKeyboardButton(
                text=obj["name"],
                callback_data=f"select_object:{group_id}:{obj['id']}"
            )
        ])

    kb.append([
        InlineKeyboardButton(text="➕ Создать объект", callback_data=f"create_object:{group_id}")
    ])

    kb.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=f"group:{group_id}")
    ])

    return InlineKeyboardMarkup(inline_keyboard=kb)