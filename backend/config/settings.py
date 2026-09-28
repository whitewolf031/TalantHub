"""
TalantHub — Django settings.
Barcha sozlamalar .env fayl orqali boshqariladi (backend/.env).
"""
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="unsafe-secret-key-change-me")
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd party
    "rest_framework",
    "rest_framework.authtoken",
    # local apps
    "apps.users",
    "apps.categories",
    "apps.announcements",
    "apps.admin_api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://talanthub:talanthub@db:5432/talanthub",
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "uz"
TIME_ZONE = env("TIME_ZONE", default="Asia/Tashkent")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Gunicorn ostida admin CSS/JS fayllarini whitenoise beradi (DEBUG=False bo'lsa ham)
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# Admin panelga boshqa domen/IP orqali kirilganda kerak bo'lishi mumkin,
# masalan: http://192.168.1.7:8000,https://admin.example.com
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "core.permissions.InternalAPIKeyPermission",
    ],
    "DEFAULT_PAGINATION_CLASS": "core.pagination.DefaultPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    # Faqat login kabi anonim endpointlarga qo'llanadi (brute-force'dan himoya)
    "DEFAULT_THROTTLE_RATES": {"anon": "20/min"},
}

# --- TalantHub maxsus sozlamalari -----------------------------------------

# Bot -> Backend so'rovlarini tekshirish uchun ichki API kalit.
# Bot ham xuddi shu qiymatni backend/.env va bot/.env ikkalasida ham bir xil
# saqlashi kerak (INTERNAL_API_KEY).
INTERNAL_API_KEY = env("INTERNAL_API_KEY", default="change-me-internal-key")

# Telegram bot tokeni — tasdiqlangan e'lonlarni kanalga yuborish uchun
# Django tomonidan to'g'ridan-to'g'ri Telegram Bot API'ga so'rov yuboriladi.
TELEGRAM_BOT_TOKEN = env("BOT_TOKEN", default="")
TELEGRAM_CHANNEL_ID = env("CHANNEL_ID", default="")  # masalan: @talanthub_channel yoki -100...

# Bitta foydalanuvchi tasdiqlangan e'londan keyin necha soatdan so'ng
# yangi e'lon joylay olishi mumkinligi.
ANNOUNCEMENT_COOLDOWN_HOURS = env.int("ANNOUNCEMENT_COOLDOWN_HOURS", default=24)
