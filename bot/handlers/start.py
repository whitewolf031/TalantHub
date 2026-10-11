import logging

from aiogram import F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.common import language_keyboard
from keyboards.main import main_menu_keyboard
from services import api_client
from services.channel import get_channel_link, is_subscribed, subscription_keyboard
from utils.texts import TEXTS, t

logger = logging.getLogger(__name__)

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    user = await api_client.get_user(message.from_user.id)
    ref_code = command.args if command.args and command.args.startswith("ref_") else None

    if user is None:
        # Birinchi marta kirmoqda — agar referal kodi bo'lsa FSM da saqlab turamiz
        if ref_code:
            await state.update_data(ref_code=ref_code)
        await message.answer(t("choose_language", "uz"), reply_markup=language_keyboard())
        return

    lang = user.get("language", "uz")
    await api_client.touch_activity(message.from_user.id)

    # Kanal obunasini tekshirish
    subscribed = await is_subscribed(message.bot, message.from_user.id)
    if not subscribed:
        channel_url = await get_channel_link(message.bot)
        await message.answer(
            t("must_subscribe_channel", lang),
            reply_markup=subscription_keyboard(lang, channel_url),
            parse_mode="HTML",
        )
        return

    await message.answer(
        t("welcome", lang, name=message.from_user.first_name or ""),
    )
    await message.answer(t("main_menu", lang), reply_markup=main_menu_keyboard(lang))


@router.callback_query(F.data.startswith("lang:"))
async def on_language_chosen(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split(":", 1)[1]
    data = await state.get_data()
    ref_code = data.get("ref_code")
    await state.clear()

    reg_res = await api_client.register_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        language=lang,
        ref_code=ref_code,
    )

    # Agar do'st taklif qilingan bo'lsa, taklif qiluvchiga bildirishnoma yuboramiz
    if reg_res and reg_res.get("referral_event"):
        event = reg_res["referral_event"]
        inviter_id = event["inviter_telegram_id"]
        inviter_lang = event.get("inviter_lang", "uz")
        try:
            await callback.bot.send_message(
                inviter_id,
                t(
                    "referral_joined_notification",
                    inviter_lang,
                    name=event.get("referred_name", "Do'stingiz"),
                    invited_count=event.get("invited_count", 0),
                    target_count=event.get("target_count", 5),
                ),
                parse_mode="HTML",
            )
            if event.get("rewarded"):
                await callback.bot.send_message(
                    inviter_id,
                    t("referral_reward_notification", inviter_lang),
                    parse_mode="HTML",
                )
        except Exception as e:
            logger.warning(f"Taklif qiluvchiga bildirishnoma yuborishda xatolik: {e}")

    # Kanal obunasini tekshirish
    subscribed = await is_subscribed(callback.bot, callback.from_user.id)
    if not subscribed:
        channel_url = await get_channel_link(callback.bot)
        await callback.message.edit_text(
            t("must_subscribe_channel", lang),
            reply_markup=subscription_keyboard(lang, channel_url),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    await callback.message.edit_text(t("welcome", lang, name=callback.from_user.first_name or ""))
    await callback.message.answer(t("main_menu", lang), reply_markup=main_menu_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "sub:check")
async def on_check_subscription(callback: CallbackQuery):
    user = await api_client.get_user(callback.from_user.id)
    lang = user.get("language", "uz") if user else "uz"

    subscribed = await is_subscribed(callback.bot, callback.from_user.id)
    if not subscribed:
        await callback.answer(t("sub_not_joined", lang), show_alert=True)
        return

    await callback.answer(t("sub_joined_success", lang))
    try:
        await callback.message.delete()
    except Exception:
        pass

    await callback.message.answer(
        t("welcome", lang, name=callback.from_user.first_name or ""),
    )
    await callback.message.answer(t("main_menu", lang), reply_markup=main_menu_keyboard(lang))


def _is_back_button(message: Message) -> bool:
    return message.text in {TEXTS["btn_back"][code] for code in ("uz", "en", "ru")}


@router.message(_is_back_button)
async def back_to_main_menu(message: Message, state: FSMContext):
    """Profil / Yordam / Tilni o'zgartirish bo'limlaridagi 'Orqaga' tugmasi."""
    await state.clear()
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

    await message.answer(t("main_menu", lang), reply_markup=main_menu_keyboard(lang))