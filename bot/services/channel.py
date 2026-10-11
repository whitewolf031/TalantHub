import logging
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import CHANNEL_ID, CHANNEL_URL
from utils.texts import t

logger = logging.getLogger(__name__)


def _format_telegram_url(val: str) -> str:
    val = (val or "").strip()
    if not val:
        return ""
    if val.startswith("http://") or val.startswith("https://"):
        return val
    if val.startswith("t.me/"):
        return f"https://{val}"
    if val.startswith("@"):
        return f"https://t.me/{val.lstrip('@')}"
    return f"https://t.me/{val}"


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


async def get_channel_link(bot: Bot = None) -> str:
    """Kanalga a'zo bo'lish havolasini oladi (birinchi navbatda env dagi CHANNEL_URL)."""
    if CHANNEL_URL:
        return _format_telegram_url(CHANNEL_URL)

    if not CHANNEL_ID:
        return "https://t.me"

    if CHANNEL_ID.startswith("@"):
        return f"https://t.me/{CHANNEL_ID.lstrip('@')}"

    if bot:
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
