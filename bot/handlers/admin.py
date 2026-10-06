from aiogram import F, Router
from aiogram.types import CallbackQuery

from config import ADMIN_IDS
from services import api_client

router = Router(name="admin")


@router.callback_query(F.data.startswith("adm:"))
async def moderate(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Sizda ruxsat yo'q.", show_alert=True)
        return

    try:
        _, action, raw_id = callback.data.split(":")
        announcement_id = int(raw_id)
    except ValueError:
        await callback.answer("Noto'g'ri so'rov.", show_alert=True)
        return

    try:
        status_code, body = await api_client.moderate_announcement(announcement_id, action)
    except Exception:
        await callback.answer("Backend bilan aloqa yo'q. Keyinroq urinib ko'ring.", show_alert=True)
        return

    if status_code == 200:
        if action == "approve":
            if body.get("status") == "waiting_payment":
                verdict = "✅ E'lon ma'qullandi, to'lov kutilmoqda"
            else:
                verdict = "✅ Tasdiqlandi va kanalga yuborildi"
        elif action == "approve-payment":
            verdict = "✅ To'lov tasdiqlandi va kanalga yuborildi"
        elif action == "reject-payment":
            verdict = "❌ To'lov rad etildi"
        else:
            verdict = "❌ Rad etildi"

        formatted_verdict = f"\n\n{verdict} — {callback.from_user.full_name}"
        if callback.message.caption is not None:
            new_caption = f"{callback.message.caption}{formatted_verdict}"[:1024]
            await callback.message.edit_caption(caption=new_caption, reply_markup=None)
        else:
            await callback.message.edit_text(
                f"{callback.message.text}{formatted_verdict}",
                reply_markup=None,
            )
        await callback.answer(verdict)
    elif status_code == 409:
        already_msg = "\n\nℹ️ Bu e'lon allaqachon ko'rib chiqilgan."
        if callback.message.caption is not None:
            new_caption = f"{callback.message.caption}{already_msg}"[:1024]
            await callback.message.edit_caption(caption=new_caption, reply_markup=None)
        else:
            await callback.message.edit_text(
                f"{callback.message.text}{already_msg}",
                reply_markup=None,
            )
        await callback.answer("Allaqachon ko'rib chiqilgan.", show_alert=True)
    elif status_code == 502:
        await callback.answer(
            "Kanalga yuborib bo'lmadi. Bot kanalda admin ekanligini va CHANNEL_ID ni tekshiring.",
            show_alert=True,
        )
    else:
        await callback.answer(f"Xatolik ({status_code}).", show_alert=True)
