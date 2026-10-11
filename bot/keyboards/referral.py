import urllib.parse
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.texts import t


def referral_inline_keyboard(lang: str, invite_link: str) -> InlineKeyboardMarkup:
    """Do'stlarga havolani ulashish tugmasi."""
    share_text = t("referral_share_message", lang, link=invite_link)
    encoded_text = urllib.parse.quote(share_text)
    share_url = f"https://t.me/share/url?url={urllib.parse.quote(invite_link)}&text={encoded_text}"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("btn_share_referral", lang),
                    url=share_url,
                )
            ]
        ]
    )
