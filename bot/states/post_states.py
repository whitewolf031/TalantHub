from aiogram.fsm.state import State, StatesGroup


class PostAnnouncement(StatesGroup):
    choosing_category = State()
    entering_name = State()
    entering_age = State()
    entering_direction = State()
    entering_technologies = State()
    entering_telegram_username = State()
    entering_phone = State()
    entering_city_from = State()
    entering_city_looking = State()
    entering_salary_amount = State()
    choosing_salary_currency = State()
    entering_contact_time = State()
    entering_purpose = State()
    confirming = State()
