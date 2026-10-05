from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from utils.texts import t

LANGUAGE_BUTTONS = {
    "🇺🇿 O'zbekcha": "uz",
    "🇬🇧 English": "en",
    "🇷🇺 Русский": "ru",
}


def language_reply_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=name) for name in LANGUAGE_BUTTONS],
            [KeyboardButton(text=t("btn_back", lang))],
        ],
        resize_keyboard=True,
    )