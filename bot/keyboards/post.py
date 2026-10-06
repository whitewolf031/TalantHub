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


def plan_selection_keyboard(lang: str, amount: int = 10000) -> InlineKeyboardMarkup:
    formatted_amount = f"{amount:,}".replace(",", " ")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("btn_plan_free", lang), callback_data="plan:free"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("btn_plan_premium", lang, amount=formatted_amount),
                    callback_data="plan:premium",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("btn_cancel", lang), callback_data="post:cancel"
                )
            ],
        ]
    )


def portfolio_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("btn_no_portfolio", lang), callback_data="portfolio:none"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("btn_cancel", lang), callback_data="post:cancel"
                )
            ],
        ]
    )


