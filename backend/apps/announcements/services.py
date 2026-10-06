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
    "waiting_payment": {
        "uz": "✅ Sizning #{id} sonli e'loningiz admin tomonidan ma'qullandi!\n\nE'lon kanalga joylanishi uchun to'lovni amalga oshiring:\n💳 Karta: {card_number}\n👤 Egasi: {card_owner}\n💰 Narx: {amount} so'm\n\n{instruction}\n\nTo'lovni amalga oshirgach, quyidagi '💳 To'lov chekini yuklash' tugmasini bosing:",
        "en": "✅ Your announcement #{id} has been approved by admin!\n\nPlease make the payment to post your announcement:\n💳 Card: {card_number}\n👤 Owner: {card_owner}\n💰 Price: {amount} UZS\n\n{instruction}\n\nAfter payment, please click the button below to upload your receipt:",
        "ru": "✅ Ваше объявление #{id} одобрено администратором!\n\nДля публикации объявления переведите оплату:\n💳 Карта: {card_number}\n👤 Владелец: {card_owner}\n💰 Сумма: {amount} сум\n\n{instruction}\n\nПосле оплаты нажмите кнопку ниже для загрузки чека:",
    },
    "payment_approved": {
        "uz": "🎉 To'lovingiz tasdiqlandi va e'loningiz kanalga joylandi!\nE'loningiz 1 oy davomida (har hafta 1 martadan) kanalga avtomatik chiqariladi.",
        "en": "🎉 Your payment was approved and announcement published to the channel!\nIt will be automatically reposted weekly for 1 month.",
        "ru": "🎉 Ваша оплата подтверждена, и объявление опубликовано на канале!\nОно будет автоматически публиковаться раз в неделю в течение 1 месяца.",
    },
    "payment_rejected": {
        "uz": "❌ To'lov chekingiz tasdiqlanmadi.",
        "en": "❌ Your payment receipt was rejected.",
        "ru": "❌ Ваш чек об оплате был отклонен.",
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

from datetime import timedelta

def build_channel_text(announcement) -> str:
    a = announcement
    action = CATEGORY_ACTION_PHRASES.get(a.category.key, a.category.name_uz.upper())
    title_prefix = "💎 PREMIUM E'LON\n" if a.is_premium else ""
    title = f"{title_prefix}🔥 {a.direction.upper()} {action}"

    lines = [
        f"{title}\n",
        f"👤 {a.full_name}",
        f"🎂 {a.age} yosh",
        f"📍 Location: {a.city_from} dan",
        f"💰 {a.salary_display()}\n",
        f"🛠 {a.technologies}\n",
        f"🌍 Hozirgi shaxar: {a.city_looking}",
        f"⏰ Murojaat vaqti: {a.contact_time_display()}\n",
        f"🎯 Maqsad: {a.purpose}\n",
        f"📱 Telefon: {a.phone_number}",
        f"💬 Telegram: {a.telegram_username}",
    ]

    if a.is_premium:
        if a.linkedin_url:
            lines.append(f"🔗 LinkedIn: {a.linkedin_url}")
        if a.portfolio_url:
            lines.append(f"💼 Portfolio: {a.portfolio_url}")

    return "\n".join(lines)

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
    token = settings.TELEGRAM_BOT_TOKEN
    if not channel_id or not token:
        logger.warning("CHANNEL_ID yoki BOT_TOKEN sozlanmagan — kanalga yuborib bo'lmadi.")
        return None

    caption = build_channel_text(announcement)

    # Agar pulli e'lon va rezyume fayl mavjud bo'lsa, sendDocument orqali yuboramiz
    if announcement.is_premium and announcement.resume_file:
        try:
            import os
            file_path = announcement.resume_file.path
            if os.path.exists(file_path):
                # Telegram caption limiti 1024 belgi
                safe_caption = caption[:1024]
                with open(file_path, "rb") as fp:
                    response = requests.post(
                        TELEGRAM_API_URL.format(token=token, method="sendDocument"),
                        data={"chat_id": channel_id, "caption": safe_caption},
                        files={"document": (os.path.basename(file_path), fp)},
                        timeout=30,
                    )
                if response.ok:
                    return response.json().get("result", {}).get("message_id")
                else:
                    logger.error("sendDocument xatosi: %s %s", response.status_code, response.text)
        except Exception:
            logger.exception("sendDocument yuborishda xatolik yuz berdi, sendMessage ga o'tiladi")

    # Oddiy e'lon yoki rezyume bo'lmasa sendMessage
    result = _telegram_call(
        "sendMessage",
        {"chat_id": channel_id, "text": caption},
    )
    return result.get("message_id") if result else None


def notify_user(announcement, kind: str, reason: str = "") -> None:
    """Foydalanuvchiga (uning tilida) natija haqida xabar yuboradi. Xato bo'lsa jim o'tadi."""
    lang = announcement.user.language if announcement.user.language in ("uz", "en", "ru") else "uz"
    text = USER_MESSAGES[kind][lang]
    if reason:
        text += f"\n\n{USER_MESSAGES['reason'][lang]}: {reason}"
    _telegram_call("sendMessage", {"chat_id": announcement.user.telegram_id, "text": text})


def notify_user_to_pay(announcement):
    from .models import PaymentSetting
    payment_setting = PaymentSetting.get_active()
    lang = announcement.user.language if announcement.user.language in ("uz", "en", "ru") else "uz"
    amount_str = f"{payment_setting.amount:,}".replace(",", " ")
    inst = getattr(payment_setting, f"instruction_{lang}", payment_setting.instruction_uz)

    text = USER_MESSAGES["waiting_payment"][lang].format(
        id=announcement.id,
        card_number=payment_setting.card_number,
        card_owner=payment_setting.card_owner,
        amount=amount_str,
        instruction=inst,
    )
    btn_text = {
        "uz": "💳 To'lov chekini yuklash",
        "en": "💳 Upload receipt",
        "ru": "💳 Загрузить чек",
    }.get(lang, "💳 To'lov chekini yuklash")

    payload = {
        "chat_id": announcement.user.telegram_id,
        "text": text,
        "reply_markup": {
            "inline_keyboard": [
                [{"text": btn_text, "callback_data": f"receipt:upload:{announcement.id}"}]
            ]
        },
    }
    _telegram_call("sendMessage", payload)


def approve_announcement(pk: int):
    """
    Kutilayotgan e'lonni tasdiqlaydi.
    - Agar premium bo'lsa: status -> WAITING_PAYMENT bo'ladi, to'lov qilish so'rovi yuboriladi.
    - Agar oddiy bo'lsa: status -> APPROVED bo'ladi va kanalga chiqariladi.
    (announcement, code) qaytaradi; code: "waiting_payment" | "ok" | "not_pending" | "channel_failed"
    """
    with transaction.atomic():
        announcement = (
            Announcement.objects.select_for_update()
            .select_related("category", "user")
            .get(pk=pk)
        )
        if announcement.status != AnnouncementStatus.PENDING:
            return announcement, "not_pending"

        if announcement.is_premium:
            announcement.status = AnnouncementStatus.WAITING_PAYMENT
            announcement.save(update_fields=["status", "updated_at"])
            notify_user_to_pay(announcement)
            return announcement, "waiting_payment"

        message_id = send_to_channel(announcement)
        if message_id is None:
            return announcement, "channel_failed"

        announcement.status = AnnouncementStatus.APPROVED
        announcement.approved_at = timezone.now()
        announcement.channel_message_id = message_id
        announcement.post_count = 1
        announcement.next_publish_date = None

        announcement.save(
            update_fields=[
                "status",
                "approved_at",
                "channel_message_id",
                "post_count",
                "next_publish_date",
                "updated_at",
            ]
        )

    notify_user(announcement, "approved")
    return announcement, "ok"


def submit_receipt(pk: int, receipt_file) -> tuple:
    """Foydalanuvchi to'lov chekini yuklaydi (status -> PAYMENT_PENDING)."""
    with transaction.atomic():
        announcement = (
            Announcement.objects.select_for_update()
            .select_related("category", "user")
            .get(pk=pk)
        )
        if announcement.status not in (AnnouncementStatus.WAITING_PAYMENT, AnnouncementStatus.PAYMENT_PENDING):
            return announcement, "invalid_status"

        announcement.payment_receipt = receipt_file
        announcement.status = AnnouncementStatus.PAYMENT_PENDING
        announcement.save(update_fields=["payment_receipt", "status", "updated_at"])

    return announcement, "ok"


def approve_payment(pk: int):
    """To'lov chekini tasdiqlash va e'lonni kanalga chiqarish."""
    with transaction.atomic():
        announcement = (
            Announcement.objects.select_for_update()
            .select_related("category", "user")
            .get(pk=pk)
        )
        if announcement.status not in (AnnouncementStatus.WAITING_PAYMENT, AnnouncementStatus.PAYMENT_PENDING):
            return announcement, "invalid_status"

        message_id = send_to_channel(announcement)
        if message_id is None:
            return announcement, "channel_failed"

        announcement.status = AnnouncementStatus.APPROVED
        announcement.approved_at = timezone.now()
        announcement.channel_message_id = message_id
        announcement.post_count = 1
        announcement.next_publish_date = timezone.now() + timedelta(days=7)
        announcement.save(
            update_fields=[
                "status",
                "approved_at",
                "channel_message_id",
                "post_count",
                "next_publish_date",
                "updated_at",
            ]
        )

    notify_user(announcement, "payment_approved")
    return announcement, "ok"


def reject_payment(pk: int, reason: str = ""):
    """To'lov chekini rad etish."""
    with transaction.atomic():
        announcement = (
            Announcement.objects.select_for_update()
            .select_related("category", "user")
            .get(pk=pk)
        )
        if announcement.status not in (AnnouncementStatus.WAITING_PAYMENT, AnnouncementStatus.PAYMENT_PENDING):
            return announcement, "invalid_status"

        announcement.status = AnnouncementStatus.REJECTED
        announcement.rejected_at = timezone.now()
        announcement.reject_reason = (reason or "")[:255]
        announcement.save(update_fields=["status", "rejected_at", "reject_reason", "updated_at"])

    notify_user(announcement, "payment_rejected", announcement.reject_reason)
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


def delete_resume(pk: int) -> bool:
    """Rezyume faylini diskdan va db dan o'chiradi."""
    try:
        announcement = Announcement.objects.get(pk=pk)
        if announcement.resume_file:
            announcement.resume_file.delete(save=False)
            announcement.resume_file = None
            announcement.resume_deleted_at = timezone.now()
            announcement.save(update_fields=["resume_file", "resume_deleted_at", "updated_at"])
            return True
    except Announcement.DoesNotExist:
        pass
    return False


def process_scheduled_posts_and_cleanup() -> dict:
    """
    1. Har 7 kunda avtomatik chiqarish (1 oyda 4 marta).
    2. 1 oy (30 kun) o'tgandan keyin avtomat rezyumeni o'chirish.
    """
    now = timezone.now()
    published_count = 0
    cleanup_count = 0

    # 1. Chiqarilishi kerak bo'lgan premium e'lonlar
    due_announcements = Announcement.objects.filter(
        is_premium=True,
        status=AnnouncementStatus.APPROVED,
        post_count__lt=4,
        next_publish_date__isnull=False,
        next_publish_date__lte=now,
    ).select_related("category", "user")

    for a in due_announcements:
        msg_id = send_to_channel(a)
        if msg_id:
            a.post_count += 1
            if a.post_count < 4:
                a.next_publish_date = now + timedelta(days=7)
            else:
                a.next_publish_date = None
            a.channel_message_id = msg_id
            a.save(update_fields=["post_count", "next_publish_date", "channel_message_id", "updated_at"])
            published_count += 1

    # 2. 1 oy (30 kun) o'tgan e'lonlarning rezyumesini avtomatik o'chirish
    one_month_ago = now - timedelta(days=30)
    expired_announcements = Announcement.objects.filter(
        is_premium=True,
        approved_at__lte=one_month_ago,
        resume_file__isnull=False,
    ).exclude(resume_file="")

    for a in expired_announcements:
        if a.resume_file:
            a.resume_file.delete(save=False)
            a.resume_file = None
            a.resume_deleted_at = now
            a.save(update_fields=["resume_file", "resume_deleted_at", "updated_at"])
            cleanup_count += 1

    return {"published": published_count, "resumes_cleaned": cleanup_count}

