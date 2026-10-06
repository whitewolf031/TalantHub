from aiogram.fsm.state import State, StatesGroup


class PostAnnouncement(StatesGroup):
    choosing_category = State()
    choosing_plan = State()
    entering_name = State()
    entering_age = State()
    entering_direction = State()
    entering_technologies = State()
    # entering_telegram_username = State()
    entering_phone = State()
    entering_city_from = State()
    entering_city_looking = State()
    entering_salary_amount = State()
    choosing_salary_currency = State()
    entering_contact_time = State()
    entering_purpose = State()
    confirming_free = State()
    entering_linkedin = State()
    entering_portfolio = State()
    uploading_resume = State()
    confirming_premium = State()
    uploading_receipt = State()


class ContactAdmin(StatesGroup):
    entering_name = State()
    entering_message = State()

