from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def group_menu_kb(group_id: int, bot_username: str):
    deep_link = f"Перейдите по ссылке что бы стать администратором:\n\n https://t.me/{bot_username}?start=add_admin_{group_id}"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📦 Изменить объект",
            callback_data=f"change_object:{group_id}"
        )],


        [InlineKeyboardButton(
            text="➕ Добавить администратора",
            switch_inline_query=deep_link
        )],

        [InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="menu:groups"
        )]
    ])