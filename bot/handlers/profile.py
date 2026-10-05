from aiogram import Router
from aiogram.types import Message

from keyboards.main import back_keyboard
from services import api_client
from utils.texts import TEXTS, t

router = Router(name="profile")

STATUS_KEY_MAP = {
    "pending": "status_pending",
    "approved": "status_approved",
    "rejected": "status_rejected",
}


def _is_profile_button(message: Message) -> bool:
    return message.text in {TEXTS["btn_profile"]["uz"], TEXTS["btn_profile"]["en"], TEXTS["btn_profile"]["ru"]}


@router.message(_is_profile_button)
async def show_profile(message: Message):
    user = await api_client.get_user(message.from_user.id)
    lang = user.get("language", "uz") if user else "uz"

    announcements = await api_client.get_my_announcements(message.from_user.id)

    if not announcements:
        await message.answer(
            f"{t('profile_title', lang)}\n\n{t('profile_no_posts', lang)}",
            reply_markup=back_keyboard(lang),
        )
        return

    lines = [t("profile_title", lang), ""]
    for item in announcements:
        status_text = t(STATUS_KEY_MAP.get(item["status"], "status_pending"), lang)
        lines.append(f"• {item['category']} — {status_text}")

    await message.answer("\n".join(lines), reply_markup=back_keyboard(lang))