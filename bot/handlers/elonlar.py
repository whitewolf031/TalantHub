from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.common import cancel_inline_keyboard, phone_request_keyboard, remove_keyboard, yes_no_keyboard
from keyboards.main import main_menu_keyboard
from keyboards.post import category_keyboard, currency_keyboard
from services import api_client
from services.notifier import notify_admins
from states.post_states import PostAnnouncement
from utils.texts import TEXTS, t
from utils.validators import (
    is_valid_age,
    is_valid_name,
    is_valid_phone,
    is_valid_salary_amount,
    parse_contact_time,
)

router = Router(name="elonlar")


async def _get_lang(telegram_id: int) -> str:
    user = await api_client.get_user(telegram_id)
    return user.get("language", "uz") if user else "uz"


def _is_new_post_button(message: Message) -> bool:
    return message.text in {TEXTS["btn_new_post"]["uz"], TEXTS["btn_new_post"]["en"], TEXTS["btn_new_post"]["ru"]}


# --- Boshlash: cooldown tekshiruvi va kategoriya tanlash -------------------

@router.message(_is_new_post_button)
async def start_new_post(message: Message, state: FSMContext):
    lang = await _get_lang(message.from_user.id)

    cooldown = await api_client.check_cooldown(message.from_user.id)
    if cooldown.get("blocked"):
        await message.answer(t("user_blocked", lang))
        return
    if not cooldown.get("can_post", True):
        remaining = cooldown.get("remaining_seconds", 0)
        hours, remainder = divmod(remaining, 3600)
        minutes, _ = divmod(remainder, 60)
        await message.answer(t("cooldown_wait", lang, hours=hours, minutes=minutes))
        return

    categories = await api_client.get_categories()
    await state.update_data(lang=lang)
    await state.set_state(PostAnnouncement.choosing_category)
    await message.answer(t("choose_category", lang), reply_markup=category_keyboard(categories, lang))


@router.callback_query(F.data == "post:cancel")
async def cancel_post(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.clear()
    await callback.message.edit_text(t("post_cancelled", lang))
    await callback.message.answer(t("main_menu", lang), reply_markup=main_menu_keyboard(lang))
    await callback.answer()


@router.message(Command("cancel"), StateFilter(PostAnnouncement))
async def cancel_post_by_command(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.clear()
    await message.answer(t("post_cancelled", lang), reply_markup=main_menu_keyboard(lang))


@router.callback_query(PostAnnouncement.choosing_category, F.data.startswith("cat:"))
async def category_chosen(callback: CallbackQuery, state: FSMContext):
    category_key = callback.data.split(":", 1)[1]
    data = await state.get_data()
    lang = data.get("lang", "uz")

    await state.update_data(category_key=category_key)
    await state.set_state(PostAnnouncement.entering_name)
    await callback.message.edit_text(t("ask_name", lang))
    await callback.answer()


# --- Ism ---------------------------------------------------------------

@router.message(PostAnnouncement.entering_name)
async def process_name(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    if not is_valid_name(message.text or ""):
        await message.answer(t("invalid_name", lang))
        return

    await state.update_data(full_name=message.text.strip())
    await state.set_state(PostAnnouncement.entering_age)
    await message.answer(t("ask_age", lang))


# --- Yosh ----------------------------------------------------------------

@router.message(PostAnnouncement.entering_age)
async def process_age(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    valid, age = is_valid_age(message.text or "")
    if not valid:
        await message.answer(t("invalid_age", lang))
        return

    await state.update_data(age=age)
    await state.set_state(PostAnnouncement.entering_direction)
    await message.answer(t("ask_direction", lang))


# --- Yo'nalish -------------------------------------------------------------

@router.message(PostAnnouncement.entering_direction)
async def process_direction(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    text = (message.text or "").strip()
    if not text:
        await message.answer(t("ask_direction", lang))
        return

    await state.update_data(direction=text)
    await state.set_state(PostAnnouncement.entering_technologies)
    await message.answer(t("ask_technologies", lang))


# --- Texnologiyalar --------------------------------------------------------

@router.message(PostAnnouncement.entering_technologies)
async def process_technologies(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    text = (message.text or "").strip()
    if not text:
        await message.answer(t("ask_technologies", lang))
        return

    # Telegram username so'ralmaydi — profildan avtomatik olinadi.
    username = message.from_user.username
    telegram_username = f"@{username}" if username else f"@id{message.from_user.id}"

    await state.update_data(technologies=text, telegram_username=telegram_username)
    await state.set_state(PostAnnouncement.entering_phone)
    await message.answer(t("ask_phone", lang), reply_markup=phone_request_keyboard(lang))

# # --- Telegram username ------------------------------------------------

# @router.message(PostAnnouncement.entering_telegram_username)
# async def process_telegram_username(message: Message, state: FSMContext):
#     data = await state.get_data()
#     lang = data.get("lang", "uz")

#     username = (message.text or "").strip()
#     if not is_valid_telegram_username(username):
#         await message.answer(t("invalid_telegram_username", lang))
#         return

#     if not username.startswith("@"):
#         username = f"@{username}"

#     await state.update_data(telegram_username=username)
#     await state.set_state(PostAnnouncement.entering_phone)
#     await message.answer(t("ask_phone", lang), reply_markup=phone_request_keyboard(lang))


# --- Telefon raqam ----------------------------------------------------------

@router.message(PostAnnouncement.entering_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = f"+{phone}"

    if not is_valid_phone(phone):
        await message.answer(t("invalid_phone", lang))
        return

    await _save_phone_and_continue(message, state, phone, lang)


@router.message(PostAnnouncement.entering_phone, F.text)
async def process_phone_text(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    phone = (message.text or "").strip()
    if not is_valid_phone(phone):
        await message.answer(t("invalid_phone", lang))
        return

    await _save_phone_and_continue(message, state, phone, lang)


async def _save_phone_and_continue(message: Message, state: FSMContext, phone: str, lang: str):
    await state.update_data(phone_number=phone)
    await state.set_state(PostAnnouncement.entering_city_from)
    await message.answer(t("ask_city_from", lang), reply_markup=remove_keyboard())


# --- Shaharlar ---------------------------------------------------------

@router.message(PostAnnouncement.entering_city_from)
async def process_city_from(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    text = (message.text or "").strip()
    if not text:
        await message.answer(t("ask_city_from", lang))
        return

    await state.update_data(city_from=text)
    await state.set_state(PostAnnouncement.entering_city_looking)
    await message.answer(t("ask_city_looking", lang))


@router.message(PostAnnouncement.entering_city_looking)
async def process_city_looking(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    text = (message.text or "").strip()
    if not text:
        await message.answer(t("ask_city_looking", lang))
        return

    await state.update_data(city_looking=text)
    await state.set_state(PostAnnouncement.entering_salary_amount)
    await message.answer(t("ask_salary_amount", lang))


# --- Oylik ---------------------------------------------------------------

@router.message(PostAnnouncement.entering_salary_amount)
async def process_salary_amount(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    valid, amount = is_valid_salary_amount(message.text or "")
    if not valid:
        await message.answer(t("invalid_salary", lang))
        return

    await state.update_data(salary_amount=amount)
    await state.set_state(PostAnnouncement.choosing_salary_currency)
    await message.answer(t("ask_salary_currency", lang), reply_markup=currency_keyboard(lang))


@router.callback_query(PostAnnouncement.choosing_salary_currency, F.data.startswith("currency:"))
async def process_salary_currency(callback: CallbackQuery, state: FSMContext):
    currency = callback.data.split(":", 1)[1]
    data = await state.get_data()
    lang = data.get("lang", "uz")

    await state.update_data(salary_currency=currency)
    await state.set_state(PostAnnouncement.entering_contact_time)
    await callback.message.edit_text(t("ask_contact_time", lang))
    await callback.answer()


# --- Murojaat vaqti ----------------------------------------------------

@router.message(PostAnnouncement.entering_contact_time)
async def process_contact_time(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    valid, start, end = parse_contact_time(message.text or "")
    if not valid:
        await message.answer(t("invalid_contact_time", lang))
        return

    await state.update_data(contact_time_start=start, contact_time_end=end)
    await state.set_state(PostAnnouncement.entering_purpose)
    await message.answer(t("ask_purpose", lang))


# --- Maqsad va preview -----------------------------------------------------

@router.message(PostAnnouncement.entering_purpose)
async def process_purpose(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    text = (message.text or "").strip()
    if not text:
        await message.answer(t("ask_purpose", lang))
        return

    await state.update_data(purpose=text)
    await state.set_state(PostAnnouncement.confirming)

    data = await state.get_data()
    preview = _build_preview(data)
    await message.answer(f"{t('preview_title', lang)}\n\n{preview}")
    await message.answer(t("confirm_send", lang), reply_markup=yes_no_keyboard(lang))


# Backend'dagi apps/announcements/services.py -> CATEGORY_ACTION_PHRASES bilan bir xil.
CATEGORY_ACTION_PHRASES = {
    "job_seeker": "ISH QIDIRMOQDA",
    "mentor_needed": "USTOZ QIDIRMOQDA",
    "employee_needed": "XODIM QIDIRMOQDA",
    "partner_needed": "HAMKOR QIDIRMOQDA",
    "student_needed": "SHOGIRD QIDIRMOQDA",
}


def _build_preview(data: dict) -> str:
    action = CATEGORY_ACTION_PHRASES.get(data.get("category_key"), "E'LON")
    title = f"🔥 {(data.get('direction') or '').upper()} {action}"

    if data.get("salary_currency") == "USD":
        salary = f"${data.get('salary_amount')}"
    else:
        salary = f"{data.get('salary_amount')} so'm"

    return (
        f"{title}\n\n"
        f"👤 {data.get('full_name')}\n"
        f"🎂 {data.get('age')} yosh\n"
        f"📍 Location: {data.get('city_from')} dan\n"
        f"💰 {salary}\n\n"
        f"🛠 {data.get('technologies')}\n\n"
        f"🌍 Hozirgi shaxar: {data.get('city_looking')}\n"
        f"⏰ Murojaat vaqti: {data.get('contact_time_start')}–{data.get('contact_time_end')}\n\n"
        f"🎯 Maqsad: {data.get('purpose')}\n\n"
        f"📱 Telefon: {data.get('phone_number')}\n"
        f"💬 Telegram: {data.get('telegram_username')}"
    )


@router.callback_query(PostAnnouncement.confirming, F.data == "confirm:no")
async def confirm_no(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.clear()
    await callback.message.edit_text(t("post_cancelled", lang))
    await callback.message.answer(t("main_menu", lang), reply_markup=main_menu_keyboard(lang))
    await callback.answer()


@router.callback_query(PostAnnouncement.confirming, F.data == "confirm:yes")
async def confirm_yes(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    payload = {
        "telegram_id": callback.from_user.id,
        "category_key": data["category_key"],
        "full_name": data["full_name"],
        "age": data["age"],
        "direction": data["direction"],
        "technologies": data["technologies"],
        "telegram_username": data["telegram_username"],
        "phone_number": data["phone_number"],
        "city_from": data["city_from"],
        "city_looking": data["city_looking"],
        "salary_amount": data["salary_amount"],
        "salary_currency": data["salary_currency"],
        "contact_time_start": data["contact_time_start"],
        "contact_time_end": data["contact_time_end"],
        "purpose": data["purpose"],
    }

    success, response = await api_client.create_announcement(payload)
    await state.clear()

    if success:
        await callback.message.edit_text(t("post_sent", lang))
        await notify_admins(callback.bot, response, callback.from_user)
    else:
        if response.get("status_code") == 403:
            await callback.message.edit_text(t("user_blocked", lang))
        elif response.get("status_code") == 429:
            remaining = response.get("body", {}).get("remaining_seconds", 0)
            hours, remainder = divmod(remaining, 3600)
            minutes, _ = divmod(remainder, 60)
            await callback.message.edit_text(t("cooldown_wait", lang, hours=hours, minutes=minutes))
        else:
            await callback.message.edit_text(t("generic_error", lang))

    await callback.message.answer(t("main_menu", lang), reply_markup=main_menu_keyboard(lang))
    await callback.answer()
