import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import admin, elonlar, help, profile, settings, start

logging.basicConfig(level=logging.INFO)


async def main():
    # Matnlarda HTML teg ishlatilmaydi va foydalanuvchi kiritgan matnlarda
    # "<" kabi belgilar bo'lishi mumkin, shuning uchun parse_mode o'rnatilmagan.
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(admin.router)
    dp.include_router(elonlar.router)
    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(settings.router)
    dp.include_router(help.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
