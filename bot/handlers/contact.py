from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.main import back_keyboard, main_menu_keyboard
from services import api_client
from services.channel import get_channel_link, is_subscribed, subscription_keyboard
from services.notifier import notify_contact_message
from states.post_states import ContactAdmin
from utils.texts import TEXTS, t

router = Router(name="contact")


async def _get_lang(telegram_id: int) -> str:
    user = await api_client.get_user(telegram_id)
    return user.get("language", "uz") if user else "uz"


def _is_contact_admin_button(message: Message) -> bool:
    return message.text in {
        TEXTS["btn_contact_admin"]["uz"],
        TEXTS["btn_contact_admin"]["en"],
        TEXTS["btn_contact_admin"]["ru"],
    }


def _is_back_button(message: Message) -> bool:
    return message.text in {
        TEXTS["btn_back"]["uz"],
        TEXTS["btn_back"]["en"],
        TEXTS["btn_back"]["ru"],
        TEXTS["btn_cancel"]["uz"],
        TEXTS["btn_cancel"]["en"],
        TEXTS["btn_cancel"]["ru"],
    }


@router.message(_is_contact_admin_button)
async def start_contact_admin(message: Message, state: FSMContext):
    lang = await _get_lang(message.from_user.id)

    subscribed = await is_subscribed(message.bot, message.from_user.id)
    if not subscribed:
        channel_url = await get_channel_link(message.bot)
        await message.answer(
            t("must_subscribe_channel", lang),
            reply_markup=subscription_keyboard(lang, channel_url),
            parse_mode="HTML",
        )
        return

    await state.clear()
    await state.update_data(lang=lang)
    await state.set_state(ContactAdmin.entering_name)

    # Foydalanuvchining telegramdagi to'liq ismini default taklif qilishimiz mumkin
    await message.answer(
        t("ask_contact_name", lang),
        reply_markup=back_keyboard(lang),
    )


@router.message(Command("cancel"), StateFilter(ContactAdmin))
@router.message(_is_back_button, StateFilter(ContactAdmin))
async def cancel_contact(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang") or await _get_lang(message.from_user.id)
    await state.clear()
    await message.answer(t("main_menu", lang), reply_markup=main_menu_keyboard(lang))


@router.message(ContactAdmin.entering_name)
async def process_contact_name(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang") or "uz"

    name = (message.text or "").strip()
    if not name or len(name) < 2:
        await message.answer(t("invalid_contact_name", lang))
        return

    await state.update_data(contact_name=name)
    await state.set_state(ContactAdmin.entering_message)
    await message.answer(t("ask_contact_message", lang))


@router.message(ContactAdmin.entering_message)
async def process_contact_message(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang") or "uz"

    text = (message.text or "").strip()
    if not text:
        await message.answer(t("invalid_contact_message", lang))
        return

    name = data.get("contact_name", message.from_user.full_name)
    await notify_contact_message(message.bot, message.from_user, name, text)

    await state.clear()
    await message.answer(t("contact_sent", lang))
    await message.answer(t("main_menu", lang), reply_markup=main_menu_keyboard(lang))
