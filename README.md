# TalantHub 🎯

Telegram orqali **ish, ustoz, xodim, hamkor va shogird** topish uchun e'lon platformasi.

```
Foydalanuvchi ──► Telegram Bot ──► Backend (Django) ──► Adminlarga Telegramda xabar
                                        ▲                        │ ✅ Tasdiqlash / ❌ Rad etish
                                        │                        ▼
              React admin panel ────────┴──────── Telegram kanaliga e'lon chiqadi
              (yoki Django admin)
```

## 1. Moderatsiya oqimi

1. Foydalanuvchi botda e'lonni to'ldiradi va **✅ Ha** bosadi → e'lon `pending` holatida saqlanadi.
2. Bot **barcha adminlarga** (`ADMIN_IDS`) e'lonni **✅ Tasdiqlash / ❌ Rad etish** tugmalari bilan yuboradi.
3. Admin **Tasdiqlash** bossa → backend e'lonni kanalga yuboradi, `approved` qiladi va foydalanuvchiga
   "e'loningiz kanalga chiqdi" deb xabar beradi. **Rad etish** bossa → foydalanuvchi xabardor qilinadi va menyuga qaytadi.
4. Xuddi shu amallarni **React admin panel** yoki **Django admin** orqali ham bajarish mumkin — uchala yo'l
   bitta mantiqdan foydalanadi (`apps/announcements/services.py`). Biri ko'rib chiqsa, boshqasidagi tugma
   "allaqachon ko'rib chiqilgan" deydi (ikki marta kanalga chiqmaydi).
5. Tasdiqlangan e'londan keyin foydalanuvchi **24 soat** qayta e'lon joylay olmaydi (`ANNOUNCEMENT_COOLDOWN_HOURS`).

## 2. Loyiha tuzilmasi

```
talanthub/
├── backend/            # Django + DRF (PostgreSQL)
│   ├── config/         # settings, urls
│   ├── core/           # ichki API kalit permission'i
│   ├── entrypoint.sh   # makemigrations, migrate, fixture, superuser, collectstatic
│   └── apps/
│       ├── users/          # BotUser
│       ├── categories/     # E'lon turlari (DB'da, admin orqali kengaytiriladi)
│       ├── announcements/  # E'lonlar, validatsiya, moderatsiya servislari, bot uchun API
│       └── admin_api/      # React panel uchun API (Token auth, faqat staff)
├── bot/                # aiogram 3.x
│   ├── handlers/       # start, elonlar, settings, profile, help, admin (moderatsiya tugmalari)
│   ├── keyboards/      # main, post, settings, common, admin
│   ├── services/       # api_client.py, notifier.py (adminlarga xabar)
│   └── utils/          # matnlar (uz/en/ru), validatorlar
├── admin-panel/        # React (Vite) moderatsiya paneli
├── docker-compose.yml
├── .env.example
└── README.md
```

Ikki xil API bor va ular alohida himoyalangan:

| API | Manzil | Himoya | Kim ishlatadi |
|---|---|---|---|
| Bot API | `/api/users`, `/api/categories`, `/api/announcements` | `X-Internal-Api-Key` header | Telegram bot |
| Admin API | `/api/admin/*` | Token (faqat `is_staff`) | React panel |

## 3. Docker bilan ishga tushirish

```bash
cp .env.example .env      # qiymatlarni to'ldiring (pastdagi 4-bo'limga qarang)
docker compose up --build
```

| Servis | Manzil |
|---|---|
| React admin panel | http://localhost:3000 |
| Django admin | http://localhost:8000/admin/ |
| Backend API | http://localhost:8000/api/ |

Birinchi ishga tushishda `entrypoint.sh` o'zi migratsiyalarni bajaradi, 5 ta standart e'lon turini yuklaydi
va `.env`dagi `DJANGO_SUPERUSER_*` bilan superuser yaratadi. **Shu login/parol bilan ikkala adminga ham kirasiz.**

## 4. Sozlash (.env)

- `BOT_TOKEN` — @BotFather'dan.
- `CHANNEL_ID` — kanal (`@username` yoki `-100...`). **Bot kanalda admin bo'lishi shart.**
- `ADMIN_IDS` — moderatorlarning Telegram ID'lari (@userinfobot orqali bilinadi). Har biri botga bir marta `/start` bosishi kerak, aks holda bot unga yozolmaydi.
- `INTERNAL_API_KEY` — `python3 -c "import secrets; print(secrets.token_hex(32))"` bilan yarating.
- `BACKEND_API_URL` — Docker'da `http://web-admin:8000/api`, lokalda `http://localhost:8000/api`.
- `DATABASE_URL` — Docker'da host `db`, lokalda `localhost`.

## 5. Lokal ishga tushirish (Docker'siz)

Har bir servis uchun alohida venv (Python 3.11/3.12 tavsiya etiladi):

```bash
# Backend
cd backend && python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# .env: DATABASE_URL ni localhost'ga moslang
python manage.py makemigrations && python manage.py migrate
python manage.py loaddata apps/categories/fixtures/categories.json
python manage.py createsuperuser
python manage.py runserver

# Bot (yangi terminal)
cd bot && python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python bot.py

# React panel (yangi terminal)
cd admin-panel && npm install && npm run dev      # http://localhost:5173
```

Dev rejimida panel `/api` so'rovlarini `http://localhost:8000` ga yo'naltiradi. Backend boshqa manzilda bo'lsa:
`VITE_PROXY_TARGET=http://192.168.1.7:8000 npm run dev`.

## 6. React admin panel imkoniyatlari

Django admin'dagi barcha asosiy amallar:

- **E'lonlar** — Kutilmoqda / Tasdiqlangan / Rad etilgan / Hammasi, qidiruv (ism, telefon, username, yo'nalish),
  tur bo'yicha filtr, batafsil ko'rish, **tasdiqlash (kanalga yuboradi)**, **rad etish (sabab bilan)**, tahrirlash, o'chirish.
- **E'lon turlari** — qo'shish, tahrirlash, faollashtirish/o'chirish, tartib (bot tugmalari avtomatik yangilanadi).
- **Foydalanuvchilar** — qidiruv, filtr, tahrirlash, bloklash/blokdan chiqarish (bloklangan foydalanuvchi e'lon joylay olmaydi), o'chirish.
- **Yangi e'lon bildirishnomasi** — panel har 15 soniyada tekshiradi: chap menyuda e'lonlar soni (🟠), sahifa
  sarlavhasida `(3) TalantHub Admin`, ekranda xabar va (ruxsat berilsa) brauzer bildirishnomasi chiqadi.

> Django'ning `Users/Groups` boshqaruvi React panelga kiritilmagan — ular uchun Django admin'dan foydalaning.

## 7. Kengaytirish

- **Yangi e'lon turi** — React panel yoki Django admin → E'lon turlari → qo'shish. Kod o'zgarmaydi.
- **Yangi til** — `bot/utils/texts.py` va `backend/apps/announcements/services.py` (`USER_MESSAGES`) ga qo'shing.
- **Yangi modul** (masalan to'lov) — `backend/apps/` ga yangi app, botga yangi `handlers/` fayl.

## 8. Xavfsizlik eslatmalari

- `.env` ni git'ga qo'shmang. Productionda `INTERNAL_API_KEY`, `DJANGO_SECRET_KEY`, superuser parolini almashtiring.
- Panel va Django admin HTTP'da ishlaydi — internetga chiqarsangiz, ularni HTTPS (nginx/Caddy) ortiga qo'ying.
- Bot hozircha polling rejimida; yuqori yuklamada webhook'ga o'tish tavsiya etiladi.
