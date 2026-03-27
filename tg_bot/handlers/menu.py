from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.main_menu import main_menu

router = Router()


@router.callback_query(F.data == "menu:employees")
async def employees(call: CallbackQuery):
    await call.message.delete()

    await call.message.answer(
        "👥 Раздел: Сотрудники\n\n В Вашем чате сотрудники должны отправить сообщение /reg ФИО\n\nпример:\n/reg Иванов Иван Иванович",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
            ]
        )
    )





@router.callback_query(F.data == "back")
async def back(call: CallbackQuery):
    await call.message.delete()

    await call.message.answer(
        "Главное меню:",
        reply_markup=await main_menu(call.from_user)
    )