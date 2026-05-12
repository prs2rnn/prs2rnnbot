from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject
from core.config import ADMIN_ID


class IsAdmin(BaseFilter):
    def __init__(self):
        self._admin_id = ADMIN_ID

    async def __call__(self, obj: TelegramObject) -> bool:
        return str(obj.from_user.id) == self._admin_id
