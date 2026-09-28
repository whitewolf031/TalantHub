from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from utils.texts import t


def main_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("btn_new_post", lang))],
            [KeyboardButton(text=t("btn_profile", lang)), KeyboardButton(text=t("btn_settings", lang))],
            [KeyboardButton(text=t("btn_help", lang))],
        ],
        resize_keyboard=True,
    )
