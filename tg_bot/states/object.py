from aiogram.fsm.state import StatesGroup, State


class CreateObject(StatesGroup):
    name = State()