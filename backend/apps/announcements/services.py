"""
E'lonni moderatsiya qilish servislari.

Tasdiqlash / rad etish uchta joydan chaqirilishi mumkin va hammasi bitta
mantiqdan foydalanadi:
  1. Telegram (admin botdagi inline tugmalarni bosadi)  -> internal API
  2. React admin panel                                  -> admin API
  3. Django admin                                       -> admin actions

Django to'g'ridan-to'g'ri Telegram Bot HTTP API'ga so'rov yuboradi, shuning
uchun bot jarayoni o'chiq bo'lsa ham kanalga yuborish ishlaydi.
"""
import logging

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import Announcement, AnnouncementStatus

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/{method}"

USER_MESSAGES = {
    "approved": {
        "uz": "✅ E'loningiz tasdiqlandi va kanalga joylandi!",
        "en": "✅ Your announcement was approved and published to the channel!",
        "ru": "✅ Ваше объявление одобрено и опубликовано в канале!",
    },
    "rejected": {
        "uz": "❌ E'loningiz moderatsiyadan o'tmadi. Ma'lumotlarni tekshirib, qayta yuborishingiz mumkin.",
        "en": "❌ Your announcement was not approved. Please check the details and submit again.",
        "ru": "❌ Ваше объявление не прошло модерацию. Проверьте данные и отправьте снова.",
    },
    "reason": {"uz": "Sabab", "en": "Reason", "ru": "Причина"},
}

CATEGORY_ACTION_PHRASES = {
    "job_seeker": "ISH QIDIRMOQDA",
    "mentor_needed": "USTOZ QIDIRMOQDA",
    "employee_needed": "XODIM QIDIRMOQDA",
    "partner_needed": "HAMKOR QIDIRMOQDA",
    "student_needed": "SHOGIRD QIDIRMOQDA",
}

def build_channel_text(announcement) -> str:
    a = announcement
    action = CATEGORY_ACTION_PHRASES.get(a.category.key, a.category.name_uz.upper())
    title = f"🔥 {a.direction.upper()} {action}"

    return (
        f"{title}\n\n"
        f"👤 {a.full_name}\n"
        f"🎂 {a.age} yosh\n"
        f"📍 Location: {a.city_from} dan\n"
        f"💰 {a.salary_display()}\n\n"
        f"🛠 {a.technologies}\n\n"
        f"🌍 Hozirgi shaxar: {a.city_looking}\n"
        f"⏰ Murojaat vaqti: {a.contact_time_display()}\n\n"
        f"🎯 Maqsad: {a.purpose}\n\n"
        f"📱 Telefon: {a.phone_number}\n"
        f"💬 Telegram: {a.telegram_username}"
    )

def _telegram_call(method: str, payload: dict):
    """Telegram Bot API'ga so'rov. Muvaffaqiyatli bo'lsa `result`, aks holda None."""
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.warning("BOT_TOKEN sozlanmagan — Telegram so'rovi yuborilmadi (%s).", method)
        return None

    try:
        response = requests.post(
            TELEGRAM_API_URL.format(token=token, method=method),
            json=payload,
            timeout=10,
        )
        if not response.ok:
            logger.error("Telegram %s xatosi: %s %s", method, response.status_code, response.text)
            return None
        return response.json().get("result")
    except requests.RequestException:
        logger.exception("Telegram %s so'rovida tarmoq xatosi", method)
        return None


def send_to_channel(announcement):
    """E'lonni kanalga yuboradi. Muvaffaqiyatli bo'lsa message_id, aks holda None."""
    channel_id = settings.TELEGRAM_CHANNEL_ID
    if not channel_id:
        logger.warning("CHANNEL_ID sozlanmagan — kanalga yuborib bo'lmadi.")
        return None

    result = _telegram_call(
        "sendMessage",
        {"chat_id": channel_id, "text": build_channel_text(announcement)},
    )
    return result.get("message_id") if result else None


def notify_user(announcement, kind: str, reason: str = "") -> None:
    """Foydalanuvchiga (uning tilida) natija haqida xabar yuboradi. Xato bo'lsa jim o'tadi."""
    lang = announcement.user.language if announcement.user.language in ("uz", "en", "ru") else "uz"
    text = USER_MESSAGES[kind][lang]
    if reason:
        text += f"\n\n{USER_MESSAGES['reason'][lang]}: {reason}"
    _telegram_call("sendMessage", {"chat_id": announcement.user.telegram_id, "text": text})


def approve_announcement(pk: int):
    """
    Kutilayotgan e'lonni tasdiqlaydi va kanalga yuboradi.
    (announcement, code) qaytaradi; code: "ok" | "not_pending" | "channel_failed"
    """
    with transaction.atomic():
        announcement = (
            Announcement.objects.select_for_update()
            .select_related("category", "user")
            .get(pk=pk)
        )
        if announcement.status != AnnouncementStatus.PENDING:
            return announcement, "not_pending"

        message_id = send_to_channel(announcement)
        if message_id is None:
            return announcement, "channel_failed"

        announcement.status = AnnouncementStatus.APPROVED
        announcement.approved_at = timezone.now()
        announcement.channel_message_id = message_id
        announcement.save(update_fields=["status", "approved_at", "channel_message_id", "updated_at"])

    notify_user(announcement, "approved")
    return announcement, "ok"


def reject_announcement(pk: int, reason: str = ""):
    """(announcement, code) qaytaradi; code: "ok" | "not_pending" """
    with transaction.atomic():
        announcement = (
            Announcement.objects.select_for_update()
            .select_related("category", "user")
            .get(pk=pk)
        )
        if announcement.status != AnnouncementStatus.PENDING:
            return announcement, "not_pending"

        announcement.status = AnnouncementStatus.REJECTED
        announcement.rejected_at = timezone.now()
        announcement.reject_reason = (reason or "")[:255]
        announcement.save(update_fields=["status", "rejected_at", "reject_reason", "updated_at"])

    notify_user(announcement, "rejected", announcement.reject_reason)
    return announcement, "ok"
