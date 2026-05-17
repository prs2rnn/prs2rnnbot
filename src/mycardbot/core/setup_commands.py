from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault


async def set_commands(bot: Bot, admin_ids: list[int]):
    user_commands = [
        BotCommand(command="start", description="Показать приветственное сообщение"),
    ]
    admin_commands = [
        *user_commands,
        BotCommand(command="admin", description="Панель администратора"),
        BotCommand(command="ban", description="Добавить пользователя в бан"),
    ]

    await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())

    for admin_id in admin_ids:
        await bot.set_my_commands(
            admin_commands, scope=BotCommandScopeChat(chat_id=admin_id)
        )
