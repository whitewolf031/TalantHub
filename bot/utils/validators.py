import re

PHONE_REGEX = re.compile(r"^\+998\d{9}$")
TELEGRAM_USERNAME_REGEX = re.compile(r"^@?[A-Za-z0-9_]{5,32}$")
NAME_REGEX = re.compile(r"^[A-Za-zА-Яа-яЁёЎўҚқҒғҲҳ' -]{2,100}$")
CONTACT_TIME_REGEX = re.compile(
    r"^(0?[0-9]|1[0-9]|2[0-3]):([0-5]\d)\s*(?:[-–]|dan)?\s*(0?[0-9]|1[0-9]|2[0-3]):([0-5]\d)(?:\s*gacha)?$",
    re.IGNORECASE,
)


def is_valid_name(value: str) -> bool:
    value = (value or "").strip()
    return bool(value) and bool(NAME_REGEX.match(value))


def is_valid_age(value: str) -> tuple[bool, int | None]:
    value = (value or "").strip()
    if not value.isdigit():
        return False, None
    age = int(value)
    if 14 <= age <= 80:
        return True, age
    return False, None


def is_valid_phone(value: str) -> bool:
    return bool(PHONE_REGEX.match((value or "").strip()))


def is_valid_telegram_username(value: str) -> bool:
    return bool(TELEGRAM_USERNAME_REGEX.match((value or "").strip()))


def is_valid_salary_amount(value: str) -> tuple[bool, float | None]:
    value = (value or "").strip().replace(",", ".")
    try:
        amount = float(value)
        if amount <= 0 or amount >= 10**10:
            return False, None
        return True, round(amount, 2)
    except ValueError:
        return False, None


def parse_contact_time(value: str) -> tuple[bool, str | None, str | None]:
    """
    '9:00-18:00' yoki '09:00-18:00' kabi vaqt oralig'ini qabul qiladi
    va 'HH:MM' (09:00, 18:00) formatida qaytaradi.
    """
    match = CONTACT_TIME_REGEX.match((value or "").strip())
    if not match:
        return False, None, None
    start_hour = int(match.group(1))
    start_min = match.group(2)
    end_hour = int(match.group(3))
    end_min = match.group(4)

    start = f"{start_hour:02d}:{start_min}"
    end = f"{end_hour:02d}:{end_min}"
    if start >= end:
        return False, None, None
    return True, start, end
