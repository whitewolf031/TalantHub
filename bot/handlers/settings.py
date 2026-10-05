from aiogram import F, Router
from aiogram.types import Message

from keyboards.main import main_menu_keyboard
from keyboards.settings import LANGUAGE_BUTTONS, language_reply_keyboard
from services import api_client
from utils.texts import TEXTS, t

router = Router(name="settings")


def _is_language_button(message: Message) -> bool:
    return message.text in {TEXTS["btn_language"][code] for code in ("uz", "en", "ru")}


@router.message(_is_language_button)
async def open_language_menu(message: Message):
    user = await api_client.get_user(message.from_user.id)
    lang = user.get("language", "uz") if user else "uz"
    await message.answer(t("choose_language", lang), reply_markup=language_reply_keyboard(lang))


@router.message(F.text.in_(set(LANGUAGE_BUTTONS)))
async def change_language(message: Message):
    new_lang = LANGUAGE_BUTTONS[message.text]
    await api_client.update_language(message.from_user.id, new_lang)
    await message.answer(t("language_saved", new_lang), reply_markup=main_menu_keyboard(new_lang))