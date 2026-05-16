from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject
from core.config import setting


class IsAdmin(BaseFilter):
    def __init__(self):
        self._admin_ids = setting.admin_ids

    async def __call__(self, obj: TelegramObject) -> bool:
        return obj.from_user.id in self._admin_ids
