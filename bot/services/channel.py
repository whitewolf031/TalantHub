import logging
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import CHANNEL_ID, CHANNEL_INVITE_LINK
from utils.texts import t

logger = logging.getLogger(__name__)


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    """Foydalanuvchi kanalga a'zo ekanligini tekshiradi."""
    if not CHANNEL_ID:
        return True

    try:
        # CHANNEL_ID int yoki str bo'lishi mumkin
        chat_id = int(CHANNEL_ID) if CHANNEL_ID.lstrip("-").isdigit() else CHANNEL_ID
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        # creator, administrator, member, restricted (is_member=True) a'zo hisoblanadi
        return member.status in ("creator", "administrator", "member", "restricted")
    except Exception as e:
        logger.warning(f"Kanal obunasini tekshirishda xatolik ({user_id}): {e}")
        # Agar bot kanalga biriktirilmagan yoki xatolik bo'lsa, foydalanuvchini bloklamaymiz
        return True


async def get_channel_link(bot: Bot) -> str:
    """Kanalga a'zo bo'lish havolasini oladi."""
    if CHANNEL_INVITE_LINK:
        return CHANNEL_INVITE_LINK

    if not CHANNEL_ID:
        return "https://t.me"

    if CHANNEL_ID.startswith("@"):
        return f"https://t.me/{CHANNEL_ID.lstrip('@')}"

    try:
        chat_id = int(CHANNEL_ID) if CHANNEL_ID.lstrip("-").isdigit() else CHANNEL_ID
        chat = await bot.get_chat(chat_id)
        if chat.username:
            return f"https://t.me/{chat.username}"
        if chat.invite_link:
            return chat.invite_link
        link = await bot.create_chat_invite_link(chat_id)
        return link.invite_link
    except Exception as e:
        logger.warning(f"Kanal havolasini olishda xatolik: {e}")
        return "https://t.me"


def subscription_keyboard(lang: str, channel_url: str) -> InlineKeyboardMarkup:
    """Majburiy obuna tugmalari."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("btn_subscribe_channel", lang),
                    url=channel_url,
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("btn_check_subscription", lang),
                    callback_data="sub:check",
                )
            ],
        ]
    )
