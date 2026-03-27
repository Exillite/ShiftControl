from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from services.api import api
from keyboards.objects import objects_kb
from states.object import CreateObject

router = Router()


# 📦 открыть список объектов
@router.callback_query(F.data.startswith("change_object:"))
async def change_object(call: CallbackQuery):
    group_id = int(call.data.split(":")[1])

    data = await api.get_objects()
    objects = data.get("data", [])

    await call.message.edit_text(
        "📦 Выберите объект:",
        reply_markup=objects_kb(objects, group_id)
    )


# 📌 выбрать объект
@router.callback_query(F.data.startswith("select_object:"))
async def select_object(call: CallbackQuery):
    _, group_id, object_id = call.data.split(":")
    group_id = int(group_id)
    object_id = int(object_id)

    await api.assign_object(group_id, object_id)

    await call.answer("✅ Объект выбран", show_alert=True)



@router.callback_query(F.data.startswith("create_object:"))
async def create_object(call: CallbackQuery, state: FSMContext):
    group_id = int(call.data.split(":")[1])

    await state.update_data(group_id=group_id)
    await state.set_state(CreateObject.name)

    await call.message.edit_text("Введите название объекта:")



@router.message(CreateObject.name)
async def save_object(message: Message, state: FSMContext):
    data = await state.get_data()
    group_id = data["group_id"]

    result = await api.create_object(message.text)

    if result.get("status") == "ok":
        obj_id = result["data"]["id"]
        await api.assign_object(group_id, obj_id)

    await state.clear()

    await message.answer("✅ Объект создан и выбран")