import re

from django.core.exceptions import ValidationError

# +998 bilan boshlanuvchi, jami 9 ta raqamdan iborat (masalan +998901234567)
PHONE_REGEX = re.compile(r"^\+998\d{9}$")

# @ bilan yoki @siz, 5-32 ta harf/raqam/pastki chiziq
TELEGRAM_USERNAME_REGEX = re.compile(r"^@?[A-Za-z0-9_]{5,32}$")

# Faqat harflar (lotin, kirill, bo'shliq va tire) — ism uchun
NAME_REGEX = re.compile(r"^[A-Za-zА-Яа-яЁёЎўҚқҒғҲҳ' -]{2,100}$")


def validate_full_name(value: str):
    value = (value or "").strip()
    if not value:
        raise ValidationError("Ism bo'sh bo'lishi mumkin emas.")
    if not NAME_REGEX.match(value):
        raise ValidationError("Ism faqat harflardan iborat bo'lishi kerak.")


def validate_phone_number(value: str):
    if not PHONE_REGEX.match(value or ""):
        raise ValidationError(
            "Telefon raqam +998XXXXXXXXX formatida bo'lishi kerak."
        )


def validate_telegram_username(value: str):
    if not TELEGRAM_USERNAME_REGEX.match(value or ""):
        raise ValidationError(
            "Telegram username noto'g'ri formatda (masalan: @username)."
        )


def validate_contact_time_range(start, end):
    if start is None or end is None:
        raise ValidationError("Murojaat vaqti to'liq kiritilishi shart.")
    if start >= end:
        raise ValidationError(
            "Murojaat vaqti oralig'i noto'g'ri: boshlanish tugashdan oldin bo'lishi kerak."
        )
