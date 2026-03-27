from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from services.api import api

router = Router()

@router.message(Command("reg"))
async def register(message: Message):
    text = message.text

    # убираем "/reg"
    parts = text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer(
            "❌ Введите ФИО\n\nПример:\n/reg Иванов Иван Иванович"
        )
        return

    full_name = parts[1].strip()

    # простая валидация
    if len(full_name.split()) < 2:
        await message.answer("❌ Укажите хотя бы имя и фамилию")
        return

    tg_id = message.from_user.id

    result = await api.create_employee(full_name, tg_id)

    if result and result.get("status") == "ok":
        await message.answer("✅ Вы зарегистрированы")
    else:
        await message.answer("❌ Ошибка регистрации")