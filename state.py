from aiogram.fsm.state import StatesGroup, State


class DateInput(StatesGroup):
    waiting_for_date = State()