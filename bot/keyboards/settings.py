from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.texts import t


def settings_language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="setlang:uz"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="setlang:en"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="setlang:ru"),
            ]
        ]
    )
