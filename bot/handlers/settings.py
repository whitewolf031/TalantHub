from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from keyboards.main import main_menu_keyboard
from keyboards.settings import settings_language_keyboard
from services import api_client
from utils.texts import TEXTS, t

router = Router(name="settings")


def _is_settings_button(message: Message) -> bool:
    return message.text in {TEXTS["btn_settings"]["uz"], TEXTS["btn_settings"]["en"], TEXTS["btn_settings"]["ru"]}


@router.message(_is_settings_button)
async def open_settings(message: Message):
    user = await api_client.get_user(message.from_user.id)
    lang = user.get("language", "uz") if user else "uz"
    await message.answer(t("choose_language", lang), reply_markup=settings_language_keyboard())


@router.callback_query(F.data.startswith("setlang:"))
async def change_language(callback: CallbackQuery):
    new_lang = callback.data.split(":", 1)[1]
    await api_client.update_language(callback.from_user.id, new_lang)

    await callback.message.edit_text(t("language_saved", new_lang))
    await callback.message.answer(t("main_menu", new_lang), reply_markup=main_menu_keyboard(new_lang))
    await callback.answer()
