from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram import Bot

from services.api import api
from keyboards.checks import check_kb

router = Router()


# 🔥 открыть проверку
@router.callback_query(F.data == "menu:checks")
async def start_check(call: CallbackQuery, bot: Bot):
    await call.message.delete()

    data = await api.get_shift_for_check(call.from_user.id)

    if data.get("status") != "ok":
        await call.message.answer("❌ Ошибка")
        return

    shift = data.get("data")

    if not shift:
        await call.message.answer("✅ Нет смен для проверки")
        return

    # 📩 пересылаем сообщение
    try:
        await bot.forward_message(
            chat_id=call.from_user.id,
            from_chat_id=shift["tg_chat_id"],
            message_id=shift["tg_message_id"]
        )
    except Exception as e:
        await call.message.answer("❌ Не удалось переслать сообщение")
        print(e)
        return

    # кнопки
    await call.message.answer(
        "Проверить смену:",
        reply_markup=check_kb(shift["id"])
    )


@router.callback_query(F.data.startswith("shift_ok:"))
async def approve_shift(call: CallbackQuery, bot: Bot):
    shift_id = int(call.data.split(":")[1])

    await api.set_shift_result(shift_id, True)

    await call.answer("✅ Подтверждено")



@router.callback_query(F.data.startswith("shift_no:"))
async def reject_shift(call: CallbackQuery, bot: Bot):
    shift_id = int(call.data.split(":")[1])

    await api.set_shift_result(shift_id, False)

    await call.answer("❌ Отклонено")
