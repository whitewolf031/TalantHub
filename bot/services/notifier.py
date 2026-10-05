import logging

from aiogram import Bot
from aiogram.types import User

from config import MODERATION_GROUP_ID, MODERATION_TOPIC_ID
from keyboards.admin import moderation_keyboard

logger = logging.getLogger(__name__)


async def notify_admins(bot: Bot, announcement: dict, sender: User) -> None:
    """
    Yangi e'lonni moderatsiya guruhidagi belgilangan mavzuga (topic) yuboradi.
    ✅/❌ tugmasini FAQAT config.ADMIN_IDS ro'yxatidagilar bosa oladi —
    buni handlers/admin.py tekshiradi (o'zgarishsiz qoladi).
    """
    if not MODERATION_GROUP_ID or not MODERATION_TOPIC_ID:
        logger.warning("MODERATION_GROUP_ID / MODERATION_TOPIC_ID sozlanmagan.")
        return

    username = f"@{sender.username}" if sender.username else "—"
    text = (
        f"🆕 Yangi e'lon #{announcement['id']} — moderatsiya kutilmoqda\n\n"
        f"{announcement['preview_text']}\n\n"
        f"👥 Yuboruvchi: {sender.full_name} ({username}), ID: {sender.id}"
    )

    try:
        await bot.send_message(
            MODERATION_GROUP_ID,
            text,
            message_thread_id=MODERATION_TOPIC_ID,
            reply_markup=moderation_keyboard(announcement["id"]),
        )
    except Exception:
        logger.exception("Moderatsiya guruhiga (topicga) xabar yuborib bo'lmadi")