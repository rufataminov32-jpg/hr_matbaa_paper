# FAQ Telegram Bot

Python + SQLite asosidagi Telegram FAQ boti. Admin panel, PDF/Word/Excel fayl yuklash imkoniyati bor.

## Fayllar

```
faq_bot/
├── bot.py           — asosiy bot kodi
├── database.py      — SQLite CRUD
├── file_reader.py   — PDF / Word / Excel o'quvchi
├── requirements.txt — kutubxonalar
└── Procfile         — Railway uchun
```

## O'rnatish

### 1. BotFather
1. Telegramda `@BotFather` ga yozing
2. `/newbot` → nom va username kiriting
3. **API Token** ni oling

### 2. Admin ID
`@userinfobot` ga `/start` yuboring → sizning ID raqamingiz chiqadi

### 3. Railway deploy
1. [railway.app](https://railway.app) ga GitHub bilan kiring
2. **New Project → Deploy from GitHub repo**
3. Ushbu fayllarni GitHub repoga yuklang
4. Railway → **Variables** bo'limiga qo'shing:
   ```
   BOT_TOKEN = 123456:ABCdef...
   ADMIN_ID  = 123456789
   ```
5. Deploy → tayyor!

## Foydalanish

| Buyruq | Kim | Nima qiladi |
|--------|-----|-------------|
| `/start` | Hammaga | Savollar ro'yxatini ko'rsatadi |
| `/admin` | Faqat admin | Boshqaruv panelini ochadi |
| `/bekor` | Admin | Joriy amalni bekor qiladi |

### Admin panel imkoniyatlari
- ➕ Savol qo'shish (qo'lda)
- 🗑 Savol o'chirish
- 📋 Barcha savollarni ko'rish
- 📂 Fayl yuborish (PDF / Word / Excel)

### Excel format (eng qulay)
| A ustun | B ustun |
|---------|---------|
| Savol matni | Javob matni |
| Ish vaqti qanday? | 9:00 dan 18:00 gacha |

Birinchi qator sarlavha — o'tkazib yuboriladi.
