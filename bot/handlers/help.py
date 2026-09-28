from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services import api_client
from utils.texts import TEXTS, t

router = Router(name="help")


def _is_help_button(message: Message) -> bool:
    return message.text in {TEXTS["btn_help"]["uz"], TEXTS["btn_help"]["en"], TEXTS["btn_help"]["ru"]}


async def _send_help(message: Message):
    user = await api_client.get_user(message.from_user.id)
    lang = user.get("language", "uz") if user else "uz"
    await message.answer(t("help_text", lang))


router.message.register(_send_help, Command("help"))
router.message.register(_send_help, _is_help_button)
