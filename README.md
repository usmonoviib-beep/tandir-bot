# 🔥 Tandir Bot — Premium Telegram Bot

Tandir ishlab chiqaruvchi korxona uchun lead-yig'uvchi, tezkor buyurtma tizimiga ega Telegram bot.

## 📁 Texnologiyalar

- Python 3.12+
- Aiogram 3.x
- SQLAlchemy 2.x (async) + SQLite (kerak bo'lsa PostgreSQL'ga o'tish oson)
- Alembic migratsiyalari
- FSM (Finite State Machine)
- Repository + Service Layer arxitekturasi
- Middleware (DB sessiya, admin auth, logging)

---

## 🚀 O'RNATISH (Windows, qadam-baqadam)

### 1. Python o'rnatish

Python 3.12+ kerak. https://www.python.org/downloads/ dan yuklab oling.
O'rnatishda **"Add Python to PATH"** belgisini bosishni unutmang.

Tekshirish:
```bash
python --version
```

### 2. Loyihani papkaga joylashtirish

`tandir_bot` papkasini o'zingizga qulay joyga (masalan `C:\tandir_bot`) ko'chiring.

### 3. Virtual muhit yaratish (tavsiya etiladi)

```bash
cd C:\tandir_bot
python -m venv venv
venv\Scripts\activate
```

### 4. Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 5. `.env` faylini sozlash

`.env` faylini ochib, quyidagilarni o'zgartiring:

```env
BOT_TOKEN=123456789:AAExampleTokenFromBotFather
ADMIN_IDS=111111111,222222222
BOT_USERNAME=mening_tandir_bot
CHANNEL_URL=https://t.me/sizning_kanal
ADMIN_TELEGRAM=https://t.me/sizning_username
ADMIN_PHONE=+998901234567
COMPANY_ADDRESS=Toshkent shahri, Chilonzor tumani, ...
```

> 💡 **BOT_TOKEN** — Telegram'da @BotFather'dan `/newbot` orqali olinadi.
> **ADMIN_IDS** — sizning shaxsiy Telegram ID'ingiz. Buni @userinfobot orqali bilib olishingiz mumkin. Bir nechta admin bo'lsa, vergul bilan yozing (bo'shliqsiz).

> ⚠️ Agar `.env` fayli bilan muammo bo'lsa (Windows'da kodlashtirish xatolari tez-tez chiqadi), `config/settings.py` faylidagi `Settings` klassi default qiymatlarini to'g'ridan-to'g'ri o'zgartirib qo'yishingiz mumkin — bot ham ishlайveradi.

### 6. Ma'lumotlar bazasini tayyorlash (Alembic)

```bash
python -m alembic upgrade head
```

Bu `tandir_bot.db` (SQLite) faylini va barcha jadvallarni yaratadi.

> Eslatma: `main.py` ham ishga tushganda jadvallarni avtomatik yaratadi (`create_tables`), shuning uchun bu qadamni o'tkazib yuborsangiz ham bot ishlайveradi. Lekin Alembic — kelajakda schema o'zgarishlarini boshqarish uchun kerak.

### 7. Botni ishga tushirish

```bash
python main.py
```

Konsolda quyidagicha xabar chiqsa — bot ishga tushdi:

```
✅ Bot muvaffaqiyatli ishga tushdi!
```

---

## 👑 ADMIN PANELDAN FOYDALANISH

1. Telegramda botingizga `/admin` buyrug'ini yuboring (faqat `.env` dagi `ADMIN_IDS` ro'yxatidagi ID'lar uchun ishlaydi).
2. Admin panel ochiladi:
   - **📦 Mahsulotlar** — kategoriya qo'shish, mahsulot qo'shish/tahrirlash/o'chirish, rasm va video yuklash
   - **📨 Buyurtmalar** — kelgan buyurtmalarni ko'rish va holatini o'zgartirish (🟡🔵🟢🔴)
   - **📊 Statistika** — foydalanuvchi va buyurtma statistikasi
   - **📢 Reklama** — barcha foydalanuvchilarga matn/rasm/video/tugmali post/forward yuborish
   - **⚙️ Sozlamalar** — joriy sozlamalarni ko'rish

### Mahsulot qo'shish tartibi:

1. 📦 Mahsulotlar → ➕ Mahsulot qo'shish
2. Kategoriyani tanlang
3. Ketma-ket so'raladi: nomi → tavsif → narx → o'lcham → sig'im → yetkazib berish ma'lumoti
4. Rasm(lar) yuboring → "✅ Rasmlar tugadi"
5. Video yuboring (yoki o'tkazib yuboring)
6. "✅ Saqlash" — mahsulot tayyor!

Standart kategoriyalar (🍞 Novvoy, 🥟 Somsa, 🌍 Yer, 🛞 Aravali, 🏡 Hovli, 🏪 Kafe, 🔥 Maxsus) bot birinchi marta ishga tushganda avtomatik qo'shiladi.

---

## 🛒 BUYURTMA OQIMI (mijoz tomonidan)

1. Mijoz "🔥 Tandirlar" → kategoriya → mahsulotni tanlaydi
2. Mahsulot sahifasida "🛒 Buyurtma berish" tugmasini bosadi
3. Bot **faqat ism va telefon raqamini** so'raydi (mahsulot avtomatik aniqlanadi)
4. Buyurtma DB ga saqlanadi va **barcha adminlarga** quyidagi formatda yuboriladi:

```
🔥 YANGI BUYURTMA
👤 Ism: ...
📞 Telefon: ...
🔥 Mahsulot: ...
🆔 Telegram ID: ...
👤 Username: ...
🕒 Sana: ...
```

---

## 🗂 PROJEKT STRUKTURASI

To'liq struktura `STRUCTURE.md` faylida keltirilgan.

```
tandir_bot/
├── main.py              ← botni ishga tushirish
├── config/settings.py   ← barcha sozlamalar
├── app/
│   ├── models/          ← SQLAlchemy modellari
│   ├── repositories/     ← DB so'rovlari (Repository Pattern)
│   ├── services/         ← biznes logika (Service Layer)
│   ├── handlers/          ← user va admin handlerlar
│   ├── keyboards/         ← klaviaturalar
│   ├── middlewares/        ← DB sessiya, admin auth, logging
│   ├── states.py           ← FSM holatlari
│   └── utils/               ← logger, helper funksiyalar
├── migrations/             ← Alembic migratsiyalari
└── logs/bot.log             ← bot loglari
```

---

## 🐘 POSTGRESQL'GA O'TISH

`.env` faylida faqat `DATABASE_URL` ni o'zgartiring:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/tandir_db
```

Va `requirements.txt`ga `asyncpg` qo'shib o'rnating:

```bash
pip install asyncpg
```

Boshqa hech narsani o'zgartirish shart emas — SQLAlchemy abstraksiyasi tufayli kod o'zgarishsiz ishlaydi.

---

## 🛠 MUAMMOLARNI HAL QILISH

- **Bot javob bermayapti** → `.env` dagi `BOT_TOKEN` to'g'ri ekanligini tekshiring.
- **Admin panel ochilmayapti** → o'zingizning Telegram ID'ingiz `ADMIN_IDS` da borligini tekshiring (vergul bilan, bo'shliqsiz).
- **Xatoliklar** → `logs/bot.log` faylini ochib ko'ring, barcha xatoliklar shu yerda yoziladi.
- **.env fayli ishlamasa** → `config/settings.py` dagi default qiymatlarni to'g'ridan-to'g'ri tahrirlang.

---

## ✅ TAYYOR FUNKSIYALAR RO'YXATI

- [x] Foydalanuvchi: katalog, kategoriya, mahsulot sahifasi (rasm+video+narx+o'lcham+sig'im+yetkazish)
- [x] 1-bosqichli tezkor buyurtma (faqat ism + telefon)
- [x] Bog'lanish bo'limi (telefon, telegram, manzil)
- [x] Kanal va "Bot haqida" bo'limlari
- [x] Admin: mahsulot CRUD + rasm/video yuklash + kategoriya boshqaruvi
- [x] Admin: buyurtmalar ro'yxati va holat boshqaruvi (🟡🔵🟢🔴)
- [x] Admin: statistika (jami/bugun/hafta/oy foydalanuvchilar, buyurtmalar)
- [x] Admin: reklama (matn/rasm/video/tugmali/forward) + yuborish statistikasi
- [x] Logging, error handling, middleware, FSM, Repository/Service Layer
- [x] Alembic migratsiyalari, PostgreSQL'ga oson o'tish
