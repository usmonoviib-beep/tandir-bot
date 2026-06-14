import asyncio
from typing import Optional
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repo import UserRepository
from app.utils.logger import logger


class BroadcastService:
    def __init__(self, session: AsyncSession, bot: Bot):
        self.user_repo = UserRepository(session)
        self.bot = bot

    async def broadcast(
        self,
        text: Optional[str] = None,
        photo_id: Optional[str] = None,
        video_id: Optional[str] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        forward_from_chat_id: Optional[int] = None,
        forward_message_id: Optional[int] = None,
    ) -> dict:
        user_ids = await self.user_repo.get_all_active_ids()
        total = len(user_ids)
        success = 0
        failed = 0

        for uid in user_ids:
            try:
                if forward_from_chat_id and forward_message_id:
                    await self.bot.forward_message(
                        chat_id=uid,
                        from_chat_id=forward_from_chat_id,
                        message_id=forward_message_id,
                    )
                elif photo_id:
                    await self.bot.send_photo(
                        chat_id=uid,
                        photo=photo_id,
                        caption=text,
                        reply_markup=reply_markup,
                        parse_mode="HTML",
                    )
                elif video_id:
                    await self.bot.send_video(
                        chat_id=uid,
                        video=video_id,
                        caption=text,
                        reply_markup=reply_markup,
                        parse_mode="HTML",
                    )
                elif text:
                    await self.bot.send_message(
                        chat_id=uid,
                        text=text,
                        reply_markup=reply_markup,
                        parse_mode="HTML",
                    )
                success += 1
            except Exception as e:
                logger.warning(f"Broadcast xato: {uid} | {e}")
                failed += 1

            await asyncio.sleep(0.05)  # Flood limit

        logger.info(f"Broadcast tugadi: {success}/{total} muvaffaqiyatli")
        return {"total": total, "success": success, "failed": failed}
