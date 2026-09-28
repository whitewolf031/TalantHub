from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.texts import t


def category_keyboard(categories: list[dict], lang: str) -> InlineKeyboardMarkup:
    """
    categories — backenddan kelgan {"key": ..., "emoji": ..., "name_uz": ...} ro'yxati.
    Dinamik: yangi kategoriya admin panelda qo'shilsa, shu yerda avtomatik chiqadi.
    """
    name_field = {"uz": "name_uz", "en": "name_en", "ru": "name_ru"}.get(lang, "name_uz")
    rows = []
    for category in categories:
        text = f"{category['emoji']} {category[name_field]}"
        rows.append([InlineKeyboardButton(text=text, callback_data=f"cat:{category['key']}")])
    rows.append([InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="post:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def currency_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 so'm (UZS)", callback_data="currency:UZS"),
                InlineKeyboardButton(text="💵 USD", callback_data="currency:USD"),
            ]
        ]
    )
