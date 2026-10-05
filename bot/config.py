import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://web-admin:8000/api")
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "change-me-internal-key")
MODERATION_GROUP_ID = int(os.getenv("MODERATION_GROUP_ID", "0") or 0)
MODERATION_TOPIC_ID = int(os.getenv("MODERATION_TOPIC_ID", "0") or 0)

# Moderator (admin) Telegram ID'lari, vergul bilan: 123456789,987654321
# Yangi e'lonlar shu adminlarga yuboriladi va faqat ular tasdiqlay/rad eta oladi.
# Har bir admin botga bir marta /start bosgan bo'lishi shart.
ADMIN_IDS = [
    int(value)
    for value in os.getenv("ADMIN_IDS", "").replace(" ", "").split(",")
    if value.lstrip("-").isdigit()
]

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN .env faylida ko'rsatilishi shart!")
