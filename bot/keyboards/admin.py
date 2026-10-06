from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def moderation_keyboard(announcement_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"adm:approve:{announcement_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"adm:reject:{announcement_id}"),
            ]
        ]
    )


def payment_moderation_keyboard(announcement_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ To'lovni tasdiqlash", callback_data=f"adm:approve-payment:{announcement_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"adm:reject-payment:{announcement_id}"),
            ]
        ]
    )

