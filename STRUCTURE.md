# Tandir Bot - Loyiha Strukturasi

```
tandir_bot/
├── .env                          # Environment o'zgaruvchilar
├── .env.example                  # Namuna env fayl
├── requirements.txt              # Kutubxonalar
├── main.py                       # Asosiy kirish nuqtasi
├── alembic.ini                   # Alembic konfiguratsiya
│
├── config/
│   └── settings.py               # Barcha sozlamalar
│
├── migrations/
│   ├── env.py
│   └── versions/
│       └── 001_initial.py
│
├── app/
│   ├── database/
│   │   └── connection.py         # DB ulanish va sessiya
│   │
│   ├── models/
│   │   ├── base.py               # Base model
│   │   ├── user.py               # Foydalanuvchi modeli
│   │   ├── product.py            # Mahsulot modeli
│   │   ├── category.py           # Kategoriya modeli
│   │   └── order.py              # Buyurtma modeli
│   │
│   ├── repositories/
│   │   ├── base.py               # Base repository
│   │   ├── user_repo.py          # User CRUD
│   │   ├── product_repo.py       # Product CRUD
│   │   ├── category_repo.py      # Category CRUD
│   │   └── order_repo.py         # Order CRUD
│   │
│   ├── services/
│   │   ├── user_service.py       # User business logic
│   │   ├── product_service.py    # Product business logic
│   │   ├── order_service.py      # Order business logic
│   │   ├── broadcast_service.py  # Reklama yuborish
│   │   └── stats_service.py      # Statistika
│   │
│   ├── handlers/
│   │   ├── user/
│   │   │   ├── start.py          # /start handler
│   │   │   ├── catalog.py        # Katalog va mahsulotlar
│   │   │   ├── order.py          # Buyurtma berish FSM
│   │   │   └── info.py           # Bog'lanish, kanal, haqida
│   │   └── admin/
│   │       ├── panel.py          # Admin panel
│   │       ├── products.py       # Mahsulot boshqaruvi
│   │       ├── orders.py         # Buyurtmalar
│   │       ├── stats.py          # Statistika
│   │       └── broadcast.py      # Reklama
│   │
│   ├── keyboards/
│   │   ├── user/
│   │   │   ├── main_menu.py      # Asosiy menyu
│   │   │   ├── catalog.py        # Katalog tugmalari
│   │   │   └── order.py          # Buyurtma tugmalari
│   │   └── admin/
│   │       ├── panel.py          # Admin panel tugmalari
│   │       ├── products.py       # Mahsulot tugmalari
│   │       └── orders.py         # Buyurtma tugmalari
│   │
│   ├── middlewares/
│   │   ├── db_middleware.py      # DB sessiya middleware
│   │   ├── auth_middleware.py    # Admin tekshirish
│   │   └── logging_middleware.py # Log middleware
│   │
│   └── utils/
│       ├── logger.py             # Logging sozlash
│       └── helpers.py            # Yordamchi funksiyalar
│
└── logs/
    └── bot.log
```
