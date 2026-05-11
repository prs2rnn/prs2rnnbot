from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from core.database import bot_db
from core.utils import load_html_content
from keyboards.user_keyboard import get_main_keyboard

user_message_router = Router()


@user_message_router.message(CommandStart())
async def start(message: Message) -> None:
    await bot_db.add_user(
        message.from_user.full_name,
        message.from_user.username,
        message.from_user.id,
    )
    text = load_html_content('start')
    await message.answer(text, reply_markup=get_main_keyboard())
