import logging

from aiogram import Bot
from aiogram.types import User

from config import ADMIN_IDS
from keyboards.admin import moderation_keyboard

logger = logging.getLogger(__name__)


async def notify_admins(bot: Bot, announcement: dict, sender: User) -> None:
    """Yangi e'lonni barcha adminlarga tasdiqlash/rad etish tugmalari bilan yuboradi."""
    if not ADMIN_IDS:
        logger.warning("ADMIN_IDS bo'sh — e'lon adminlarga yuborilmadi (faqat web panelda ko'rinadi).")
        return

    username = f"@{sender.username}" if sender.username else "—"
    text = (
        f"🆕 Yangi e'lon #{announcement['id']} — moderatsiya kutilmoqda\n\n"
        f"{announcement['preview_text']}\n\n"
        f"👥 Yuboruvchi: {sender.full_name} ({username}), ID: {sender.id}"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id, text, reply_markup=moderation_keyboard(announcement["id"])
            )
        except Exception:
            # Admin botga /start bosmagan yoki botni bloklagan bo'lishi mumkin
            logger.exception("Adminga (%s) xabar yuborib bo'lmadi", admin_id)
