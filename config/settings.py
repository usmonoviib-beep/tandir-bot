from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import os


class Settings(BaseSettings):
    # Bot
    BOT_TOKEN: str = "YOUR_BOT_TOKEN_HERE"
    BOT_USERNAME: str = "tandir_bot"

    # Adminlar
    ADMIN_IDS: str = "123456789"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./tandir_bot.db"

    # Kanal va kontaktlar
    CHANNEL_URL: str = "https://t.me/your_channel"
    ADMIN_TELEGRAM: str = "https://t.me/admin_username"
    ADMIN_PHONE: str = "+998901234567"
    COMPANY_ADDRESS: str = "Toshkent shahri, Chilonzor tumani"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Bot haqida matn
    BOT_ABOUT: str = (
        "🔥 <b>Tandir zavodi</b>\n\n"
        "Biz 10 yildan ortiq tajribaga ega tandir ishlab chiqaruvchi korxonamiz.\n\n"
        "✅ Yuqori sifatli materiallar\n"
        "✅ Professional ustalar\n"
        "✅ Kafolat bilan\n"
        "✅ Yetkazib berish xizmati\n\n"
        "📞 Telefon: +998901234567\n"
        "📍 Manzil: Toshkent shahri"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def admin_ids_list(self) -> List[int]:
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]


settings = Settings()


# Agar .env fayl bo'lmasa ham ishlaydi
# Config orqali o'zgartirish mumkin:
# BOT_TOKEN ni to'g'ridan-to'g'ri settings.BOT_TOKEN = "..." orqali
