from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.common import cancel_inline_keyboard, phone_request_keyboard, remove_keyboard, yes_no_keyboard
from keyboards.main import main_menu_keyboard
from keyboards.post import (
    category_keyboard,
    currency_keyboard,
    plan_selection_keyboard,
    portfolio_keyboard,
    premium_found_action_keyboard,
)
from services import api_client
from services.notifier import notify_admins, notify_payment_receipt
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

    try:
        payment_info = await api_client.get_payment_settings()
    except Exception:
        payment_info = {"amount": 10000, "card_number": "", "card_owner": ""}

    amount = payment_info.get("amount", 10000)
    await state.update_data(category_key=category_key, payment_info=payment_info)
    await state.set_state(PostAnnouncement.choosing_plan)

    amount_str = f"{amount:,}".replace(",", " ")
    await callback.message.edit_text(
        t("choose_plan", lang, amount=amount_str),
        reply_markup=plan_selection_keyboard(lang, amount),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(PostAnnouncement.choosing_plan, F.data == "plan:free")
async def choose_free_plan(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    cooldown = await api_client.check_cooldown(callback.from_user.id, is_premium=False)
    if not cooldown.get("can_post", True):
        remaining = cooldown.get("remaining_seconds", 0)
        hours, remainder = divmod(remaining, 3600)
        minutes, _ = divmod(remainder, 60)
        await callback.message.answer(
            t("cooldown_free_plan", lang, hours=hours, minutes=minutes),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    await state.update_data(is_premium=False)
    await state.set_state(PostAnnouncement.entering_name)
    await callback.message.edit_text(t("ask_name", lang))
    await callback.answer()


@router.callback_query(PostAnnouncement.choosing_plan, F.data == "plan:premium")
async def choose_premium_plan(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    await state.update_data(is_premium=True)
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


# --- Maqsad va davom etish -------------------------------------------------

@router.message(PostAnnouncement.entering_purpose)
async def process_purpose(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    text = (message.text or "").strip()
    if not text:
        await message.answer(t("ask_purpose", lang))
        return

    await state.update_data(purpose=text)
    data = await state.get_data()

    if data.get("is_premium"):
        # Pullik (Premium) tarif tanlangan — qo'shimcha maydonlarga o'tamiz
        await state.set_state(PostAnnouncement.entering_linkedin)
        await message.answer(t("ask_linkedin", lang))
    else:
        # Tekin (Oddiy) tarif tanlangan — o'zgarmasdan preview va tasdiqlash
        preview = _build_preview(data)
        await message.answer(f"{t('preview_title', lang)}\n\n{preview}")
        await state.set_state(PostAnnouncement.confirming_free)
        await message.answer(t("confirm_send", lang), reply_markup=yes_no_keyboard(lang))


# --- Oddiy (Tekin) e'lonni tasdiqlash --------------------------------------

@router.callback_query(PostAnnouncement.confirming_free, F.data == "confirm:no")
async def confirm_free_no(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.clear()
    await callback.message.edit_text(t("post_cancelled", lang))
    await callback.message.answer(t("main_menu", lang), reply_markup=main_menu_keyboard(lang))
    await callback.answer()


@router.callback_query(PostAnnouncement.confirming_free, F.data == "confirm:yes")
async def confirm_free_yes(callback: CallbackQuery, state: FSMContext):
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
        "is_premium": False,
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


# --- Premium e'lon: LinkedIn, Portfolio, Resume, Confirmation, Receipt -----

@router.message(PostAnnouncement.entering_linkedin)
async def process_linkedin(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    text = (message.text or "").strip()
    if not (text.startswith("http://") or text.startswith("https://")) or "linkedin.com" not in text.lower():
        await message.answer(t("invalid_linkedin", lang))
        return

    await state.update_data(linkedin_url=text)
    await state.set_state(PostAnnouncement.entering_portfolio)
    await message.answer(t("ask_portfolio", lang), reply_markup=portfolio_keyboard(lang))


@router.callback_query(PostAnnouncement.entering_portfolio, F.data == "portfolio:none")
async def process_portfolio_none_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    await state.update_data(portfolio_url="")
    await state.set_state(PostAnnouncement.uploading_resume)
    await callback.message.edit_text(t("ask_resume", lang))
    await callback.answer()


@router.message(PostAnnouncement.entering_portfolio, F.text)
async def process_portfolio_text(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    text = (message.text or "").strip()
    none_variants = {"yo'q", "yoq", "yo`q", "yo’q", "yo - q", "none", "no", "нет", "net", "-"}
    if text.lower() in none_variants:
        await state.update_data(portfolio_url="")
        await state.set_state(PostAnnouncement.uploading_resume)
        await message.answer(t("ask_resume", lang))
        return

    if not (text.startswith("http://") or text.startswith("https://")):
        await message.answer(t("invalid_portfolio", lang), reply_markup=portfolio_keyboard(lang))
        return

    await state.update_data(portfolio_url=text)
    await state.set_state(PostAnnouncement.uploading_resume)
    await message.answer(t("ask_resume", lang))


@router.message(PostAnnouncement.uploading_resume, F.document)
async def process_resume_document(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    doc = message.document

    fname = (doc.file_name or "").lower()
    if not any(fname.endswith(ext) for ext in (".pdf", ".doc", ".docx")):
        await message.answer(t("invalid_resume", lang))
        return

    if doc.file_size and doc.file_size > 2 * 1024 * 1024:
        await message.answer(t("invalid_resume", lang))
        return

    await state.update_data(
        resume_file_id=doc.file_id,
        resume_file_name=doc.file_name or "resume.pdf",
    )

    data = await state.get_data()
    preview = _build_preview(data)
    await message.answer(f"{t('preview_title', lang)}\n\n{preview}")
    await state.set_state(PostAnnouncement.confirming_premium)
    await message.answer(t("confirm_send", lang), reply_markup=yes_no_keyboard(lang))


@router.message(PostAnnouncement.uploading_resume)
async def process_resume_invalid(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await message.answer(t("invalid_resume", lang))


@router.callback_query(PostAnnouncement.confirming_premium, F.data == "confirm:no")
async def confirm_premium_no(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.clear()
    await callback.message.edit_text(t("post_cancelled", lang))
    await callback.message.answer(t("main_menu", lang), reply_markup=main_menu_keyboard(lang))
    await callback.answer()


@router.callback_query(PostAnnouncement.confirming_premium, F.data == "confirm:yes")
async def confirm_premium_yes(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    resume_bytes = None
    resume_filename = data.get("resume_file_name", "resume.pdf")
    if data.get("resume_file_id"):
        try:
            resume_file_info = await callback.bot.get_file(data["resume_file_id"])
            resume_stream = await callback.bot.download_file(resume_file_info.file_path)
            resume_bytes = resume_stream.read()
        except Exception:
            resume_bytes = None

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
        "is_premium": True,
        "linkedin_url": data.get("linkedin_url", ""),
        "portfolio_url": data.get("portfolio_url", ""),
    }

    success, response = await api_client.create_announcement(
        payload,
        resume_bytes=resume_bytes,
        resume_filename=resume_filename,
    )
    await state.clear()

    if success:
        await callback.message.edit_text(t("post_sent_premium", lang))
        await notify_admins(
            callback.bot,
            response,
            callback.from_user,
            resume_file_id=data.get("resume_file_id"),
        )
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


@router.callback_query(F.data.startswith("receipt:upload:"))
async def handle_receipt_upload_button(callback: CallbackQuery, state: FSMContext):
    announcement_id = int(callback.data.split(":", 2)[2])
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(announcement_id=announcement_id)
    await state.set_state(PostAnnouncement.uploading_receipt)
    await callback.message.reply(t("ask_receipt_upload", lang))
    await callback.answer()


@router.message(PostAnnouncement.uploading_receipt, F.photo | F.document)
async def process_receipt(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    announcement_id = data.get("announcement_id")

    if not announcement_id:
        active_ann = await api_client.get_waiting_payment_announcement(message.from_user.id)
        if active_ann:
            announcement_id = active_ann["id"]

    if not announcement_id:
        await message.answer(t("no_waiting_announcement", lang))
        return

    if message.photo:
        receipt_file_id = message.photo[-1].file_id
        receipt_filename = "receipt.jpg"
        is_receipt_doc = False
    elif message.document:
        receipt_file_id = message.document.file_id
        receipt_filename = message.document.file_name or "receipt.jpg"
        is_receipt_doc = True
    else:
        await message.answer(t("invalid_receipt", lang))
        return

    try:
        receipt_file_info = await message.bot.get_file(receipt_file_id)
        receipt_stream = await message.bot.download_file(receipt_file_info.file_path)
        receipt_bytes = receipt_stream.read()
    except Exception:
        receipt_bytes = None

    if not receipt_bytes:
        await message.answer(t("generic_error", lang))
        return

    success, response = await api_client.submit_receipt(
        announcement_id, receipt_bytes, receipt_filename
    )
    await state.clear()

    if success:
        await message.answer(t("receipt_received", lang), reply_markup=main_menu_keyboard(lang))
        await notify_payment_receipt(
            message.bot,
            response,
            message.from_user,
            receipt_file_id=receipt_file_id,
            is_receipt_doc=is_receipt_doc,
        )
    else:
        await message.answer(t("generic_error", lang), reply_markup=main_menu_keyboard(lang))


@router.message(F.photo | F.document, StateFilter(None))
async def auto_receipt_handler(message: Message, state: FSMContext):
    """Foydalanuvchi tugmani bosmasdan to'g'ridan-to'g'ri chek yuborsa."""
    active_ann = await api_client.get_waiting_payment_announcement(message.from_user.id)
    if active_ann:
        await state.update_data(announcement_id=active_ann["id"])
        await process_receipt(message, state)


@router.message(PostAnnouncement.uploading_receipt)
async def process_receipt_invalid(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await message.answer(t("invalid_receipt", lang))


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
    is_premium = data.get("is_premium", False)
    title_prefix = "💎 PREMIUM E'LON\n" if is_premium else ""
    title = f"{title_prefix}🔥 {(data.get('direction') or '').upper()} {action}"

    if data.get("salary_currency") == "USD":
        salary = f"${data.get('salary_amount')}"
    else:
        salary = f"{data.get('salary_amount')} so'm"

    lines = [
        f"{title}\n",
        f"👤 {data.get('full_name')}",
        f"🎂 {data.get('age')} yosh",
        f"📍 Location: {data.get('city_from')} dan",
        f"💰 {salary}\n",
        f"🛠 {data.get('technologies')}\n",
        f"🌍 Ish qidirayotgan shahar: {data.get('city_looking')}",
        f"⏰ Murojaat vaqti: {data.get('contact_time_start')}–{data.get('contact_time_end')}\n",
        f"🎯 Maqsad: {data.get('purpose')}\n",
        f"📱 Telefon: {data.get('phone_number')}",
        f"💬 Telegram: {data.get('telegram_username')}",
    ]

    if is_premium:
        if data.get("linkedin_url"):
            lines.append(f"🔗 LinkedIn: {data.get('linkedin_url')}")
        if data.get("portfolio_url"):
            lines.append(f"💼 Portfolio: {data.get('portfolio_url')}")
        if data.get("resume_file_id"):
            lines.append("📄 Rezyume: biriktirilgan")

    return "\n".join(lines)


# --- 7 kundan keyingi "Topdingizmi?" so'rovi handlerlari -----------------

@router.callback_query(F.data.startswith("found:no:"))
async def handle_found_no(callback: CallbackQuery):
    lang = await _get_lang(callback.from_user.id)
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await callback.message.answer(t("found_no_response", lang))
    await callback.answer()


@router.callback_query(F.data.startswith("found:yes:"))
async def handle_found_yes(callback: CallbackQuery):
    lang = await _get_lang(callback.from_user.id)
    raw_id = callback.data.split(":")[2]
    try:
        announcement_id = int(raw_id)
    except ValueError:
        await callback.answer()
        return

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    success, res = await api_client.mark_announcement_found(announcement_id)
    if not success:
        await callback.message.answer(t("generic_error", lang))
        await callback.answer()
        return

    is_premium = res.get("is_premium", False)
    if is_premium:
        await callback.message.answer(
            t("found_premium_ask_action", lang),
            reply_markup=premium_found_action_keyboard(announcement_id, lang),
        )
    else:
        await callback.message.answer(t("found_free_success", lang))
    await callback.answer()


@router.callback_query(F.data.startswith("prem_action:continue:"))
async def handle_prem_continue(callback: CallbackQuery):
    lang = await _get_lang(callback.from_user.id)
    raw_id = callback.data.split(":")[2]
    try:
        announcement_id = int(raw_id)
    except ValueError:
        await callback.answer()
        return

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    success, _ = await api_client.premium_found_action(announcement_id, "continue")
    if success:
        await callback.message.answer(t("prem_continue_success", lang))
    else:
        await callback.message.answer(t("generic_error", lang))
    await callback.answer()


@router.callback_query(F.data.startswith("prem_action:delete:"))
async def handle_prem_delete(callback: CallbackQuery):
    lang = await _get_lang(callback.from_user.id)
    raw_id = callback.data.split(":")[2]
    try:
        announcement_id = int(raw_id)
    except ValueError:
        await callback.answer()
        return

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    success, _ = await api_client.premium_found_action(announcement_id, "delete")
    if success:
        await callback.message.answer(t("prem_deleted_success", lang))
    else:
        await callback.message.answer(t("generic_error", lang))
    await callback.answer()



