from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram import Bot

from services.api import api
from keyboards.group_detail import group_menu_kb

router = Router()


@router.callback_query(F.data.startswith("group:"))
async def open_group(call: CallbackQuery, bot: Bot):
    group_id = int(call.data.split(":")[1])

    await call.message.delete()

    group_data = await api.get_group(group_id)
    admins_data = await api.get_group_admins(group_id)

    if group_data.get("status") != "ok":
        await call.message.answer("❌ Ошибка загрузки группы")
        return

    group = group_data["data"]
    admins = admins_data.get("data", [])

    # название группы
    try:
        chat = await bot.get_chat(group["tg_chat_id"])
        title = chat.title
    except:
        title = f"ID: {group['tg_chat_id']}"

    # объект
    object_text = "❌ Не выбран"
    if group.get("object_id"):
        objs = await api.get_objects()
        for o in objs.get("data", []):
            if o["id"] == group["object_id"]:
                object_text = o["name"]

    # админы
    admins_text = "Нет"
    if admins:
        lines = []
        for a in admins:
            try:
                user = await bot.get_chat(a["tg_user_id"])
                name = user.full_name
                username = f"@{user.username}" if user.username else ""
                lines.append(f"{name} {username if len(username) > 2 else ''}")
            except:
                lines.append(f"ID: {a['tg_user_id']}")
        admins_text = "\n".join(lines)

    me = await bot.get_me()

    text = (
        f"📂 {title}\n\n"
        f"📦 Объект: {object_text}\n\n"
        f"👤 Администраторы:\n{admins_text}"
    )

    await call.message.answer(
        text,
        reply_markup=group_menu_kb(group_id, me.username)
    )