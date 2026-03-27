from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
import os

from keyboards.main_menu import main_menu
from services.api import api

router = Router()


@router.message(CommandStart())
async def start(message: Message, command: CommandStart):
    args = command.args

    if message.chat.type in ["group", "supergroup", "channel"]:
        return


    if args:
        if args.startswith("add_admin_"):
            try:
                group_id = int(args.split("_")[-1])
                user_id = message.from_user.id

                result = await api.create_group_admin(group_id, user_id)

                if result and result.get("status") == "ok":
                    await message.answer("✅ Вы добавлены как администратор")
                else:
                    await message.answer("❌ Ошибка добавления")

            except Exception as e:
                await message.answer("❌ Неверная ссылка")
                print(f"Deep link error: {e}")

        # return
    

    await message.answer(
        "👋 Добро пожаловать!\n\n",
        reply_markup=await main_menu(message.from_user)
    )

