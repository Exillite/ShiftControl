from aiogram.fsm.state import StatesGroup, State


class SetWorkTime(StatesGroup):
    time = State()