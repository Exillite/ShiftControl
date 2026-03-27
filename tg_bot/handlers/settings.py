from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from services.api import api
from keyboards.settings import settings_kb
from states.settings import SetWorkTime

import re

router = Router()



@router.callback_query(F.data == "menu:settings")
async def open_settings(call: CallbackQuery):
    await call.message.delete()

    data = await api.get_work_time()

    if data.get("status") == "ok":
        time = data["data"]["time"]
    else:
        time = "не задано"

    await call.message.answer(
        f"⚙️ Настройки\n\n⏰ Время окончания смены: {time}",
        reply_markup=settings_kb()
    )



@router.callback_query(F.data == "set_time")
async def set_time(call: CallbackQuery, state: FSMContext):
    await state.set_state(SetWorkTime.time)

    await call.message.edit_text(
        "Введите время в формате HH:MM\n\nПример: 23:30"
    )



@router.message(SetWorkTime.time)
async def save_time(message: Message, state: FSMContext):
    time_text = message.text.strip()


    if not re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", time_text):
        await message.answer("❌ Неверный формат. Введите HH:MM (например 23:30)")
        return

    result = await api.set_work_time(time_text)

    if result.get("status") == "ok":
        await message.answer("✅ Сохранено")
    else:
        await message.answer("❌ Ошибка сохранения")

    await state.clear()