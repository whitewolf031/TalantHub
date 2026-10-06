import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import admin, contact, elonlar, help, profile, settings, start
from services import api_client

logging.basicConfig(level=logging.INFO)


async def scheduler_task():
    """
    Davriy tekshiruv: har 10 daqiqada 7 kunlik avto-postlarni kanalga yuboradi
    va 1 oydan oshgan rezyumelarni avtomatik o'chiradi.
    """
    while True:
        try:
            res = await api_client.run_scheduler()
            if res.get("published") or res.get("resumes_cleaned"):
                logging.info(f"Scheduler natijasi: {res}")
        except Exception:
            logging.exception("Scheduler bajarilishida xatolik")
        await asyncio.sleep(600)  # har 10 daqiqada


async def main():
    # Matnlarda HTML teg ishlatilmaydi va foydalanuvchi kiritgan matnlarda
    # "<" kabi belgilar bo'lishi mumkin, shuning uchun parse_mode o'rnatilmagan.
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(admin.router)
    dp.include_router(contact.router)
    dp.include_router(elonlar.router)
    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(settings.router)
    dp.include_router(help.router)

    # Fon vazifasi (scheduler)ni ishga tushirish
    asyncio.create_task(scheduler_task())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
