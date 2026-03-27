from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram import Bot

from services.api import api
from keyboards.groups import groups_keyboard

router = Router()


@router.callback_query(F.data == "menu:groups")
async def show_groups(call: CallbackQuery, bot: Bot):
    await call.message.delete()

    data = await api.get_groups()

    if data.get("status") != "ok":
        await call.message.answer("❌ Ошибка загрузки групп")
        return

    groups = data.get("data", [])


    me = await bot.get_me()
    bot_username = me.username

    enriched_groups = []

    for g in groups:
        tg_chat_id = g["tg_chat_id"]

        try:
            chat = await bot.get_chat(tg_chat_id)
            title = chat.title or f"ID: {tg_chat_id}"
        except Exception:
            title = f"ID: {tg_chat_id}"

        enriched_groups.append({
            **g,
            "title": title
        })

    await call.message.answer(
        "📂 Выберите группу:",
        reply_markup=groups_keyboard(enriched_groups, bot_username)
    )