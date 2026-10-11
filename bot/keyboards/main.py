from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from utils.texts import t


def main_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("btn_new_post", lang))],
            [KeyboardButton(text=t("btn_referral", lang))],
            [
                KeyboardButton(text=t("btn_profile", lang)),
                KeyboardButton(text=t("btn_contact_admin", lang)),
            ],
            [
                KeyboardButton(text=t("btn_help", lang)),
            ],
            [
                KeyboardButton(text=t("btn_language", lang)),
            ]
        ],
        resize_keyboard=True,
    )


def back_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """Profil / Yordam / Tilni o'zgartirish bo'limlarida pastda faqat 'Orqaga' tugmasi turadi."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("btn_back", lang))]],
        resize_keyboard=True,
    )