from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from typing import Union

from config.settings import settings


class IsAdmin(BaseFilter):
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        return event.from_user.id in settings.admin_ids_list
