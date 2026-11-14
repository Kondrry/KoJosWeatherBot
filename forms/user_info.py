from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    city = State()
    city_week = State()
    fav_city = State()
    # location = State()