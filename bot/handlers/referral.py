import logging
from aiogram import F, Router
from aiogram.types import Message

from keyboards.referral import referral_inline_keyboard
from services import api_client
from services.channel import get_channel_link, is_subscribed, subscription_keyboard
from utils.texts import TEXTS, t

logger = logging.getLogger(__name__)

router = Router(name="referral")


def _is_referral_button(message: Message) -> bool:
    return message.text in {
        TEXTS["btn_referral"]["uz"],
        TEXTS["btn_referral"]["en"],
        TEXTS["btn_referral"]["ru"],
    }


@router.message(_is_referral_button)
async def open_referral_section(message: Message):
    # 1. Kanal a'zoligini tekshirish
    subscribed = await is_subscribed(message.bot, message.from_user.id)
    user = await api_client.get_user(message.from_user.id)
    lang = user.get("language", "uz") if user else "uz"

    if not subscribed:
        channel_url = await get_channel_link(message.bot)
        await message.answer(
            t("must_subscribe_channel", lang),
            reply_markup=subscription_keyboard(lang, channel_url),
            parse_mode="HTML",
        )
        return

    # 2. API dan referral holatini olish
    try:
        data = await api_client.get_referral_status(message.from_user.id)
    except Exception as e:
        logger.exception("Referral holatini olishda xatolik")
        await message.answer(t("generic_error", lang))
        return

    status = data.get("status")

    # Agar yangi yaratish mumkin bo'lsa, avtomat yaratamiz
    if status == "can_create":
        ok, new_data = await api_client.create_referral_campaign(message.from_user.id)
        if ok:
            data = new_data
            status = "active"
        else:
            await message.answer(t("generic_error", lang))
            return

    # Faol kampaniya
    if status == "active":
        me = await message.bot.get_me()
        bot_username = me.username
        code = data.get("code", "")
        link = f"https://t.me/{bot_username}?start={code}"

        remaining = data.get("remaining_seconds", 0)
        days, rem = divmod(remaining, 86400)
        hours, _ = divmod(rem, 3600)

        invited_count = data.get("invited_count", 0)
        target_count = data.get("target_count", 5)

        text = t(
            "referral_active_info",
            lang,
            invited_count=invited_count,
            target_count=target_count,
            days=days,
            hours=hours,
            link=link,
        )

        await message.answer(
            text,
            reply_markup=referral_inline_keyboard(lang, link),
            parse_mode="HTML",
        )
        return

    # Cooldown (1 oylik muddat hali tugamagan)
    if status == "cooldown":
        remaining = data.get("remaining_seconds", 0)
        days, rem = divmod(remaining, 86400)
        hours, _ = divmod(rem, 3600)
        free_posts = data.get("free_premium_posts", 0)

        text = t(
            "referral_cooldown_info",
            lang,
            days=days,
            hours=hours,
            free_posts=free_posts,
        )
        await message.answer(text, parse_mode="HTML")
        return

    await message.answer(t("generic_error", lang))
