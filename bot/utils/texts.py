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
    "btn_language": {"uz": "🌐 Tilni o'zgartirish", "en": "🌐 Change language", "ru": "🌐 Сменить язык"},
    "btn_back": {"uz": "⬅️ Orqaga", "en": "⬅️ Back", "ru": "⬅️ Назад"},
    "btn_help": {"uz": "ℹ️ Yordam", "en": "ℹ️ Help", "ru": "ℹ️ Помощь"},
    "btn_contact_admin": {"uz": "✍️ Admin bilan bog'lanish", "en": "✍️ Contact Admin", "ru": "✍️ Связаться с админом"},
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
    "choose_plan": {
        "uz": (
            "🎯 E'lon tarifini tanlang:\n\n"
            "🌟 <b>Oddiy (Bepul)</b> — e'lon 1 marta kanalga chiqariladi.\n\n"
            "💎 <b>Premium (Pullik — {amount} so'm)</b>:\n"
            "• LinkedIn va Portfolio havolalari\n"
            "• Rezyume (PDF/DOC) fayli biriktiriladi\n"
            "• 1 oy davomida 4 marta (har hafta 1 martadan) kanalga avtomatik chiqariladi!"
        ),
        "en": (
            "🎯 Choose announcement plan:\n\n"
            "🌟 <b>Standard (Free)</b> — published once to the channel.\n\n"
            "💎 <b>Premium ({amount} UZS)</b>:\n"
            "• LinkedIn and Portfolio links\n"
            "• Resume (PDF/DOC) attached\n"
            "• Published 4 times a month (weekly) automatically!"
        ),
        "ru": (
            "🎯 Выберите тариф объявления:\n\n"
            "🌟 <b>Обычный (Бесплатно)</b> — публикуется 1 раз в канале.\n\n"
            "💎 <b>Премиум ({amount} сум)</b>:\n"
            "• Ссылки на LinkedIn и Портфолио\n"
            "• Прикрепление резюме (PDF/DOC)\n"
            "• Публикуется 4 раза в месяц (каждую неделю) автоматически!"
        ),
    },
    "btn_plan_free": {"uz": "🌟 Oddiy (Bepul)", "en": "🌟 Standard (Free)", "ru": "🌟 Обычный (Бесплатно)"},
    "btn_plan_premium": {"uz": "💎 Premium ({amount} so'm)", "en": "💎 Premium ({amount} UZS)", "ru": "💎 Премиум ({amount} сум)"},

    "ask_linkedin": {
        "uz": "🔗 LinkedIn profilingiz havolasini yuboring (masalan: https://linkedin.com/in/...):",
        "en": "🔗 Enter your LinkedIn profile link (e.g. https://linkedin.com/in/...):",
        "ru": "🔗 Отправьте ссылку на ваш профиль в LinkedIn (например: https://linkedin.com/in/...):",
    },
    "invalid_linkedin": {
        "uz": "❗️Noto'g'ri havola. Iltimos, to'liq LinkedIn URL manzilini kiriting.",
        "en": "❗️Invalid link. Please enter a valid LinkedIn URL.",
        "ru": "❗️Некорректная ссылка. Введите правильный URL профиля LinkedIn.",
    },
    "ask_portfolio": {
        "uz": "💼 Portfolio havolangizni yuboring (GitHub, Behance, shaxsiy sayt va h.k.) yoki yo'q bo'lsa pastdagi tugmani bosing / 'yo'q' deb yozing:",
        "en": "💼 Enter your portfolio link (GitHub, Behance, website, etc.) or click the button below / type 'no':",
        "ru": "💼 Отправьте ссылку на ваше портфолио (GitHub, Behance, сайт и т.д.) или нажмите кнопку ниже / напишите 'нет':",
    },
    "btn_no_portfolio": {
        "uz": "❌ Yo'q (Portfolio mavjud emas)",
        "en": "❌ None (No portfolio)",
        "ru": "❌ Нет (Портфолио отсутствует)",
    },
    "invalid_portfolio": {
        "uz": "❗️Noto'g'ri havola. Iltimos, to'liq URL manzil kiriting (masalan: https://...) yoki yo'q bo'lsa 'yo'q' deb yozing.",
        "en": "❗️Invalid link. Please enter a valid URL (e.g. https://...) or type 'no'.",
        "ru": "❗️Некорректная ссылка. Введите правильный URL (например: https://...) или напишите 'нет'.",
    },
    "ask_resume": {
        "uz": "📄 Rezyume faylingizni yuboring (Faqat PDF yoki DOC/DOCX formatda, maksimal 2 MB):",
        "en": "📄 Send your resume file (PDF or DOC/DOCX only, max 2 MB):",
        "ru": "📄 Отправьте файл резюме (только PDF или DOC/DOCX, макс. 2 МБ):",
    },
    "invalid_resume": {
        "uz": "❗️Faqat PDF yoki DOC/DOCX formatdagi fayl yuboring (hajmi 2 MB dan oshmasin).",
        "en": "❗️Only PDF or DOC/DOCX files are accepted (max 2 MB).",
        "ru": "❗️Принимаются только файлы PDF или DOC/DOCX (макс. 2 МБ).",
    },
    "payment_instruction": {
        "uz": (
            "💳 <b>To'lov ma'lumotlari</b>\n\n"
            "Plastik karta: <code>{card_number}</code>\n"
            "Karta egasi: <b>{card_owner}</b>\n"
            "To'lov summasi: <b>{amount} so'm</b>\n\n"
            "ℹ️ {instruction}\n\n"
            "Iltimos, to'lov cheki skrinshotini (rasm yoki fayl ko'rinishida) shu yerga yuboring 👇"
        ),
        "en": (
            "💳 <b>Payment Details</b>\n\n"
            "Card number: <code>{card_number}</code>\n"
            "Card holder: <b>{card_owner}</b>\n"
            "Amount: <b>{amount} UZS</b>\n\n"
            "ℹ️ {instruction}\n\n"
            "Please send the receipt screenshot (as photo or file) here 👇"
        ),
        "ru": (
            "💳 <b>Данные для оплаты</b>\n\n"
            "Номер карты: <code>{card_number}</code>\n"
            "Владелец карты: <b>{card_owner}</b>\n"
            "Сумма оплаты: <b>{amount} сум</b>\n\n"
            "ℹ️ {instruction}\n\n"
            "Пожалуйста, отправьте скриншот чека (в виде фото или файла) сюда 👇"
        ),
    },
    "invalid_receipt": {
        "uz": "❗️Iltimos, to'lov cheki skrinshotini (rasm yoki fayl shaklida) yuboring.",
        "en": "❗️Please send a valid receipt screenshot (photo or file).",
        "ru": "❗️Пожалуйста, отправьте скриншот чека (фото или файл).",
    },
    "confirm_send": {"uz": "Yuborishni tasdiqlaysizmi?", "en": "Do you confirm sending?", "ru": "Подтверждаете отправку?"},
    "post_sent": {
        "uz": "✅ E'loningiz yuborildi va admin tomonidan tekshirilmoqda. Tasdiqlansa, kanalga chiqadi.",
        "en": "✅ Your announcement was sent and is being reviewed by the admin. It will be published once approved.",
        "ru": "✅ Ваше объявление отправлено и проверяется администратором. После одобрения оно будет опубликовано.",
    },
    "post_sent_premium": {
        "uz": (
            "✅ E'loningiz tekshirish uchun adminga yuborildi!\n\n"
            "Admin e'loningizni ma'qullaganidan so'ng, to'lov uchun rekvizitlar yuboriladi."
        ),
        "en": (
            "✅ Your announcement has been submitted for admin review!\n\n"
            "Once approved by the admin, payment details will be sent to you."
        ),
        "ru": (
            "✅ Ваше объявление отправлено на проверку администратору!\n\n"
            "После одобрения администратором вам будут отправлены реквизиты для оплаты."
        ),
    },
    "receipt_received": {
        "uz": (
            "✅ To'lov cheki qabul qilindi va adminga yuborildi!\n\n"
            "Admin to'lovni tasdiqlashi bilan e'loningiz kanalga joylanadi."
        ),
        "en": (
            "✅ Payment receipt received and sent to admin!\n\n"
            "Your announcement will be published to the channel as soon as payment is confirmed."
        ),
        "ru": (
            "✅ Чек об оплате принят и отправлен администратору!\n\n"
            "После подтверждения оплаты ваше объявление сразу появится на канале."
        ),
    },
    "ask_receipt_upload": {
        "uz": "Iltimos, to'lov cheki skrinshotini (rasm yoki fayl ko'rinishida) shu yerga yuboring 👇",
        "en": "Please send the payment receipt screenshot (photo or file) here 👇",
        "ru": "Пожалуйста, отправьте скриншот чека (фото или файл) сюда 👇",
    },
    "no_waiting_announcement": {
        "uz": "To'lov kutilayotgan e'lon topilmadi. Avval e'loningiz admin tomonidan ma'qullanishini kuting.",
        "en": "No announcement awaiting payment found. Please wait until admin approves your announcement.",
        "ru": "Не найдено объявлений, ожидающих оплаты. Дождитесь подтверждения от администратора.",
    },
    "ask_contact_name": {
        "uz": "✍️ Ism va familiyangizni kiriting:",
        "en": "✍️ Enter your full name:",
        "ru": "✍️ Введите ваше имя и фамилию:",
    },
    "invalid_contact_name": {
        "uz": "❗️Ism bo'sh bo'lishi mumkin emas.",
        "en": "❗️Name cannot be empty.",
        "ru": "❗️Имя не может быть пустым.",
    },
    "ask_contact_message": {
        "uz": "✉️ Administratorlar uchun xabaringizni yozing:",
        "en": "✉️ Write your message for the administrators:",
        "ru": "✉️ Напишите ваше сообщение для администраторов:",
    },
    "invalid_contact_message": {
        "uz": "❗️Xabar matni bo'sh bo'lishi mumkin emas.",
        "en": "❗️Message cannot be empty.",
        "ru": "❗️Сообщение не может быть пустым.",
    },
    "contact_sent": {
        "uz": "✅ Xabaringiz administratorlarga yuborildi. Tez orada siz bilan bog'lanamiz!",
        "en": "✅ Your message has been sent to the administrators. We will contact you soon!",
        "ru": "✅ Ваше сообщение отправлено администраторам. Мы свяжемся с вами в ближайшее время!",
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
