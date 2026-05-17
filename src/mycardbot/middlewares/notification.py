import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, TelegramObject, User
from core.config import setting
from core.database import bot_db


class NewUserNotificationMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        result = await handler(event, data)

        if event.message is not None and event.message.text == '/start':
            user: User = data.get('event_from_user')
            user_data = {
                'user_id': user.id,
                'full_name': user.full_name,
                'username': user.username,
            }
            is_exists = await bot_db.add_user(
                user_data['full_name'],
                user_data['username'],
                user_data['user_id'],
            )
            if not is_exists:
                await self.send_notification(user_data)
        return result

    async def send_notification(self, user_data: dict):
        text = (
            f'🆕 Новый пользователь в базе!\n\n'
            f'ID: {user_data['user_id']}\n'
            f'Имя: {user_data['full_name']}\n'
            f'Username: @{user_data['username']}'
        )
        try:
            await self.bot.send_message(chat_id=setting.channel_id, text=text)
            logging.info('Notification sent to private channel')
        except Exception as e:
            logging.error(f'Error: {e}')
