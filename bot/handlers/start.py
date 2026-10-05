from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from keyboards.common import language_keyboard
from keyboards.main import main_menu_keyboard
from services import api_client
from utils.texts import TEXTS, t
from aiogram.fsm.context import FSMContext

router = Router(name="start")

@router.message(CommandStart())
async def cmd_start(message: Message):
    user = await api_client.get_user(message.from_user.id)

    if user is None:
        # Birinchi marta kirmoqda — til tanlashni so'raymiz.
        await message.answer(t("choose_language", "uz"), reply_markup=language_keyboard())
        return

    lang = user.get("language", "uz")
    await api_client.touch_activity(message.from_user.id)
    await message.answer(
        t("welcome", lang, name=message.from_user.first_name or ""),
    )
    await message.answer(t("main_menu", lang), reply_markup=main_menu_keyboard(lang))


@router.callback_query(F.data.startswith("lang:"))
async def on_language_chosen(callback: CallbackQuery):
    lang = callback.data.split(":", 1)[1]

    await api_client.register_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        language=lang,
    )

    await callback.message.edit_text(t("welcome", lang, name=callback.from_user.first_name or ""))
    await callback.message.answer(t("main_menu", lang), reply_markup=main_menu_keyboard(lang))
    await callback.answer()

def _is_back_button(message: Message) -> bool:
    return message.text in {TEXTS["btn_back"][code] for code in ("uz", "en", "ru")}


@router.message(_is_back_button)
async def back_to_main_menu(message: Message, state: FSMContext):
    """Profil / Yordam / Tilni o'zgartirish bo'limlaridagi 'Orqaga' tugmasi."""
    await state.clear()
    user = await api_client.get_user(message.from_user.id)
    lang = user.get("language", "uz") if user else "uz"
    await message.answer(t("main_menu", lang), reply_markup=main_menu_keyboard(lang))