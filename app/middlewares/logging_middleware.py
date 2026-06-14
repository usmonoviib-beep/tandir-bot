from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from app.utils.logger import logger


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        user_id = user.id if user else "unknown"

        if isinstance(event, Message):
            text = event.text or event.caption or "[media]"
            logger.debug(f"MSG | user={user_id} | {text[:80]}")
        elif isinstance(event, CallbackQuery):
            logger.debug(f"CALLBACK | user={user_id} | {event.data}")

        try:
            return await handler(event, data)
        except Exception as e:
            logger.exception(f"Handler xatosi | user={user_id} | {e}")
            raise
