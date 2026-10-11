from aiogram import Router
from aiogram.types import Message

from keyboards.main import back_keyboard
from services import api_client
from services.channel import get_channel_link, is_subscribed, subscription_keyboard
from utils.texts import TEXTS, t

router = Router(name="profile")

STATUS_KEY_MAP = {
    "pending": "status_pending",
    "waiting_payment": "status_pending",
    "payment_pending": "status_pending",
    "approved": "status_approved",
    "rejected": "status_rejected",
}


def _is_profile_button(message: Message) -> bool:
    return message.text in {TEXTS["btn_profile"]["uz"], TEXTS["btn_profile"]["en"], TEXTS["btn_profile"]["ru"]}


@router.message(_is_profile_button)
async def show_profile(message: Message):
    user = await api_client.get_user(message.from_user.id)
    lang = user.get("language", "uz") if user else "uz"

    subscribed = await is_subscribed(message.bot, message.from_user.id)
    if not subscribed:
        channel_url = await get_channel_link(message.bot)
        await message.answer(
            t("must_subscribe_channel", lang),
            reply_markup=subscription_keyboard(lang, channel_url),
            parse_mode="HTML",
        )
        return

    announcements = await api_client.get_my_announcements(message.from_user.id)
    free_posts = user.get("free_premium_posts", 0) if user else 0

    lines = [t("profile_title", lang), ""]
    if free_posts > 0:
        lines.append(f"🎁 <b>Bepul Premium e'lonlaringiz:</b> {free_posts} ta\n")

    if not announcements:
        lines.append(t("profile_no_posts", lang))
        await message.answer(
            "\n".join(lines),
            reply_markup=back_keyboard(lang),
            parse_mode="HTML",
        )
        return

    for item in announcements:
        status_text = t(STATUS_KEY_MAP.get(item["status"], "status_pending"), lang)
        lines.append(f"• {item['category']} — {status_text}")

    await message.answer("\n".join(lines), reply_markup=back_keyboard(lang), parse_mode="HTML")