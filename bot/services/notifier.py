import logging

from aiogram import Bot
from aiogram.types import User

from config import CONTACT_TOPIC_ID, MODERATION_GROUP_ID, MODERATION_TOPIC_ID, PAYMENTS_TOPIC_ID
from keyboards.admin import moderation_keyboard, payment_moderation_keyboard

logger = logging.getLogger(__name__)


async def notify_admins(
    bot: Bot,
    announcement: dict,
    sender: User,
    resume_file_id: str | None = None,
) -> None:
    """
    Yangi e'lonni moderatsiya guruhidagi E'lonlar mavzusiga (MODERATION_TOPIC_ID) yuboradi.
    Agar rezyume fayl bo'lsa, hujjat sifatida ilova qilinadi.
    """
    if not MODERATION_GROUP_ID or not MODERATION_TOPIC_ID:
        logger.warning("MODERATION_GROUP_ID / MODERATION_TOPIC_ID sozlanmagan.")
        return

    username = f"@{sender.username}" if sender.username else "—"
    prefix = "🆕 💎 Yangi premium e'lon" if announcement.get("is_premium") else "🆕 Yangi e'lon"
    text = (
        f"{prefix} #{announcement['id']} — moderatsiya kutilmoqda\n\n"
        f"{announcement['preview_text']}\n\n"
        f"👥 Yuboruvchi: {sender.full_name} ({username}), ID: {sender.id}"
    )
    keyboard = moderation_keyboard(announcement["id"])

    try:
        if resume_file_id:
            await bot.send_document(
                MODERATION_GROUP_ID,
                document=resume_file_id,
                caption=text[:1024],
                message_thread_id=MODERATION_TOPIC_ID,
                reply_markup=keyboard,
            )
        else:
            await bot.send_message(
                MODERATION_GROUP_ID,
                text,
                message_thread_id=MODERATION_TOPIC_ID,
                reply_markup=keyboard,
            )
    except Exception:
        logger.exception("Moderatsiya guruhiga (topicga) xabar yuborib bo'lmadi")


async def notify_payment_receipt(
    bot: Bot,
    announcement: dict,
    sender: User,
    receipt_file_id: str,
    is_receipt_doc: bool = False,
) -> None:
    """
    To'lov chekini faqat To'lovlar mavzusiga (PAYMENTS_TOPIC_ID) yuboradi.
    """
    if not MODERATION_GROUP_ID or not PAYMENTS_TOPIC_ID:
        logger.warning("MODERATION_GROUP_ID / PAYMENTS_TOPIC_ID sozlanmagan.")
        return

    username = f"@{sender.username}" if sender.username else "—"
    caption = (
        f"💳 To'lov cheki — E'lon #{announcement['id']}\n\n"
        f"👤 Yuboruvchi: {sender.full_name} ({username}), ID: {sender.id}\n"
        f"📋 Yo'nalish: {announcement.get('direction', '')}\n"
        f"💎 Premium e'lon uchun to'lov skrinshoti.\n\n"
        f"Iltimos, to'lovni tekshirib tasdiqlang."
    )
    safe_caption = caption[:1024]
    keyboard = payment_moderation_keyboard(announcement["id"])

    try:
        if is_receipt_doc:
            await bot.send_document(
                MODERATION_GROUP_ID,
                document=receipt_file_id,
                caption=safe_caption,
                message_thread_id=PAYMENTS_TOPIC_ID,
                reply_markup=keyboard,
            )
        else:
            await bot.send_photo(
                MODERATION_GROUP_ID,
                photo=receipt_file_id,
                caption=safe_caption,
                message_thread_id=PAYMENTS_TOPIC_ID,
                reply_markup=keyboard,
            )
    except Exception:
        logger.exception("To'lov guruhiga (topicga) chek yuborib bo'lmadi")


async def notify_contact_message(
    bot: Bot,
    sender: User,
    name: str,
    message_text: str,
) -> None:
    """
    Foydalanuvchining 'Admin bilan bog'lanish' xabarini CONTACT_TOPIC_ID ga yuboradi.
    """
    if not MODERATION_GROUP_ID or not CONTACT_TOPIC_ID:
        logger.warning("MODERATION_GROUP_ID / CONTACT_TOPIC_ID sozlanmagan.")
        return

    username = f"@{sender.username}" if sender.username else "—"
    text = (
        f"📩 Yangi murojaat (Admin bilan bog'lanish)\n\n"
        f"👤 Ismi: {name}\n"
        f"💬 Telegram: {username} (ID: {sender.id})\n\n"
        f"📝 Xabar:\n{message_text}"
    )

    try:
        await bot.send_message(
            MODERATION_GROUP_ID,
            text,
            message_thread_id=CONTACT_TOPIC_ID,
        )
    except Exception:
        logger.exception("Aloqa guruhiga (topicga) xabar yuborib bo'lmadi")