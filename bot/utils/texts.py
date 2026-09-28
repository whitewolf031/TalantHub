"""
Oddiy i18n lug'at: uz / en / ru.
Yangi matn qo'shish uchun har uch tilga ham kalitni qo'shing.
"""

TEXTS = {
    "welcome": {
        "uz": "👋 Assalomu alaykum, {name}! TalantHub botiga xush kelibsiz.",
        "en": "👋 Hello, {name}! Welcome to TalantHub bot.",
        "ru": "👋 Здравствуйте, {name}! Добро пожаловать в TalantHub бот.",
    },
    "choose_language": {
        "uz": "🌐 Tilni tanlang:",
        "en": "🌐 Choose your language:",
        "ru": "🌐 Выберите язык:",
    },
    "language_saved": {
        "uz": "✅ Til o'zbekcha qilib saqlandi.",
        "en": "✅ Language set to English.",
        "ru": "✅ Язык сохранён: русский.",
    },
    "main_menu": {
        "uz": "Quyidagi bo'limlardan birini tanlang 👇",
        "en": "Choose one of the options below 👇",
        "ru": "Выберите один из разделов ниже 👇",
    },
    "btn_new_post": {"uz": "📢 E'lon joylash", "en": "📢 Post an ad", "ru": "📢 Разместить объявление"},
    "btn_profile": {"uz": "👤 Profil", "en": "👤 Profile", "ru": "👤 Профиль"},
    "btn_settings": {"uz": "⚙️ Sozlamalar", "en": "⚙️ Settings", "ru": "⚙️ Настройки"},
    "btn_help": {"uz": "ℹ️ Yordam", "en": "ℹ️ Help", "ru": "ℹ️ Помощь"},
    "btn_back": {"uz": "⬅️ Orqaga", "en": "⬅️ Back", "ru": "⬅️ Назад"},
    "btn_cancel": {"uz": "🚫 Bekor qilish", "en": "🚫 Cancel", "ru": "🚫 Отмена"},
    "btn_yes": {"uz": "✅ Ha", "en": "✅ Yes", "ru": "✅ Да"},
    "btn_no": {"uz": "❌ Yo'q", "en": "❌ No", "ru": "❌ Нет"},
    "btn_share_phone": {"uz": "📱 Raqamni yuborish", "en": "📱 Share phone number", "ru": "📱 Отправить номер"},

    "help_text": {
        "uz": (
            "ℹ️ TalantHub — ish, ustoz, xodim, hamkor va shogird topish uchun "
            "e'lon platformasi.\n\n"
            "📢 E'lon joylash — yangi e'lon yuborish\n"
            "👤 Profil — sizning e'lonlaringiz holati\n"
            "⚙️ Sozlamalar — tilni o'zgartirish\n\n"
            "Har qanday vaqtda /cancel buyrug'i bilan jarayonni bekor qilishingiz mumkin."
        ),
        "en": (
            "ℹ️ TalantHub — an announcement platform to find a job, mentor, "
            "employee, partner or student.\n\n"
            "📢 Post an ad — send a new announcement\n"
            "👤 Profile — status of your announcements\n"
            "⚙️ Settings — change language\n\n"
            "You can cancel any process with /cancel."
        ),
        "ru": (
            "ℹ️ TalantHub — платформа объявлений для поиска работы, "
            "наставника, сотрудника, партнёра или ученика.\n\n"
            "📢 Разместить объявление — отправить новое объявление\n"
            "👤 Профиль — статус ваших объявлений\n"
            "⚙️ Настройки — сменить язык\n\n"
            "Вы можете отменить процесс командой /cancel."
        ),
    },

    "choose_category": {
        "uz": "Qaysi turdagi e'lon joylamoqchisiz?",
        "en": "What type of announcement do you want to post?",
        "ru": "Какой тип объявления вы хотите разместить?",
    },
    "cooldown_wait": {
        "uz": "⏳ Siz yaqinda e'lon joylagansiz. Yangi e'lon uchun {hours}s {minutes}d kuting.",
        "en": "⏳ You already posted recently. Please wait {hours}h {minutes}m for a new post.",
        "ru": "⏳ Вы недавно разместили объявление. Подождите {hours}ч {minutes}м для нового.",
    },
    "user_blocked": {
        "uz": "🚫 Sizning hisobingiz bloklangan. Savollar bo'lsa, administrator bilan bog'laning.",
        "en": "🚫 Your account is blocked. Please contact the administrator.",
        "ru": "🚫 Ваш аккаунт заблокирован. Свяжитесь с администратором.",
    },
    "ask_name": {"uz": "👤 Ismingizni kiriting:", "en": "👤 Enter your name:", "ru": "👤 Введите ваше имя:"},
    "invalid_name": {
        "uz": "❗️Ism noto'g'ri. Faqat harflardan foydalaning va bo'sh qoldirmang.",
        "en": "❗️Invalid name. Use letters only, it cannot be empty.",
        "ru": "❗️Некорректное имя. Используйте только буквы, поле не может быть пустым.",
    },
    "ask_age": {"uz": "🎂 Yoshingizni kiriting (faqat raqam):", "en": "🎂 Enter your age (numbers only):", "ru": "🎂 Введите ваш возраст (только цифры):"},
    "invalid_age": {
        "uz": "❗️Yosh 14 dan 80 gacha bo'lgan raqam bo'lishi kerak.",
        "en": "❗️Age must be a number between 14 and 80.",
        "ru": "❗️Возраст должен быть числом от 14 до 80.",
    },
    "ask_direction": {"uz": "💼 Yo'nalishingizni kiriting (masalan: Backend Developer):", "en": "💼 Enter your field (e.g. Backend Developer):", "ru": "💼 Введите направление (например: Backend Developer):"},
    "ask_technologies": {"uz": "🛠 Biladigan texnologiyalaringizni vergul bilan yozing:", "en": "🛠 List technologies you know, separated by commas:", "ru": "🛠 Перечислите технологии через запятую:"},
    "ask_telegram_username": {
        "uz": "💬 Telegram username'ingizni kiriting (masalan: @username):",
        "en": "💬 Enter your Telegram username (e.g. @username):",
        "ru": "💬 Введите ваш Telegram username (например: @username):",
    },
    "invalid_telegram_username": {
        "uz": "❗️Username noto'g'ri formatda. Masalan: @username",
        "en": "❗️Invalid username format. Example: @username",
        "ru": "❗️Неверный формат username. Пример: @username",
    },
    "ask_phone": {
        "uz": "📱 Telefon raqamingizni tugma orqali yuboring yoki qo'lda +998XXXXXXXXX ko'rinishida yozing:",
        "en": "📱 Share your phone number using the button, or type it as +998XXXXXXXXX:",
        "ru": "📱 Отправьте номер телефона кнопкой или введите вручную как +998XXXXXXXXX:",
    },
    "invalid_phone": {
        "uz": "❗️Telefon raqam +998XXXXXXXXX formatida bo'lishi kerak.",
        "en": "❗️Phone number must be in +998XXXXXXXXX format.",
        "ru": "❗️Номер телефона должен быть в формате +998XXXXXXXXX.",
    },
    "ask_city_from": {"uz": "📍 Qaysi shahardan siz?", "en": "📍 Which city are you from?", "ru": "📍 Из какого вы города?"},
    "ask_city_looking": {"uz": "🔎 Qaysi shaharda imkoniyat qidiryapsiz?", "en": "🔎 Which city are you looking for opportunities in?", "ru": "🔎 В каком городе вы ищете возможность?"},
    "ask_salary_amount": {"uz": "💰 Kutilayotgan oylik miqdorini kiriting (faqat raqam):", "en": "💰 Enter the expected salary amount (numbers only):", "ru": "💰 Введите ожидаемую зарплату (только число):"},
    "invalid_salary": {"uz": "❗️Miqdor faqat raqam bo'lishi kerak.", "en": "❗️Amount must be a number.", "ru": "❗️Сумма должна быть числом."},
    "ask_salary_currency": {"uz": "💱 Valyutani tanlang:", "en": "💱 Choose currency:", "ru": "💱 Выберите валюту:"},
    "ask_contact_time": {
        "uz": "⏰ Murojaat vaqtini aniq kiriting (masalan: 09:00-18:00):",
        "en": "⏰ Enter exact contact time (e.g. 09:00-18:00):",
        "ru": "⏰ Введите точное время для связи (например: 09:00-18:00):",
    },
    "invalid_contact_time": {
        "uz": "❗️Format noto'g'ri. Aniq vaqt oralig'ini kiriting, masalan: 09:00-18:00",
        "en": "❗️Invalid format. Enter an exact time range, e.g. 09:00-18:00",
        "ru": "❗️Неверный формат. Введите точный диапазон времени, например: 09:00-18:00",
    },
    "ask_purpose": {"uz": "🎯 Maqsadingizni qisqacha yozing:", "en": "🎯 Briefly describe your purpose:", "ru": "🎯 Кратко опишите вашу цель:"},
    "preview_title": {"uz": "📋 E'loningiz shunday ko'rinadi:", "en": "📋 Your announcement preview:", "ru": "📋 Предпросмотр вашего объявления:"},
    "confirm_send": {"uz": "Yuborishni tasdiqlaysizmi?", "en": "Do you confirm sending?", "ru": "Подтверждаете отправку?"},
    "post_sent": {
        "uz": "✅ E'loningiz yuborildi va admin tomonidan tekshirilmoqda. Tasdiqlansa, kanalga chiqadi.",
        "en": "✅ Your announcement was sent and is being reviewed by the admin. It will be published once approved.",
        "ru": "✅ Ваше объявление отправлено и проверяется администратором. После одобрения оно будет опубликовано.",
    },
    "post_cancelled": {
        "uz": "🚫 E'lon joylash bekor qilindi.",
        "en": "🚫 Posting an announcement was cancelled.",
        "ru": "🚫 Размещение объявления отменено.",
    },
    "generic_error": {
        "uz": "⚠️ Xatolik yuz berdi, keyinroq urinib ko'ring.",
        "en": "⚠️ Something went wrong, please try again later.",
        "ru": "⚠️ Произошла ошибка, попробуйте позже.",
    },
    "profile_title": {"uz": "👤 Sizning profilingiz", "en": "👤 Your profile", "ru": "👤 Ваш профиль"},
    "profile_no_posts": {
        "uz": "Sizda hali e'lonlar yo'q.",
        "en": "You don't have any announcements yet.",
        "ru": "У вас пока нет объявлений.",
    },
    "status_pending": {"uz": "🕓 Kutilmoqda", "en": "🕓 Pending", "ru": "🕓 На рассмотрении"},
    "status_approved": {"uz": "✅ Tasdiqlangan", "en": "✅ Approved", "ru": "✅ Одобрено"},
    "status_rejected": {"uz": "❌ Rad etilgan", "en": "❌ Rejected", "ru": "❌ Отклонено"},
}


def t(key: str, lang: str = "uz", **kwargs) -> str:
    lang = lang if lang in ("uz", "en", "ru") else "uz"
    template = TEXTS.get(key, {}).get(lang, key)
    return template.format(**kwargs) if kwargs else template
