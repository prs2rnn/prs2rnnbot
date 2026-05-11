from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from core.utils import load_html_content
from filters.check_admin import IsAdmin
from keyboards.admin_keyboard import get_main_keyboard

admin_message_router = Router()


@admin_message_router.message(Command('admin'), IsAdmin())
async def list(message: Message) -> None:
    text = load_html_content('admin')
    text = text.replace('{name}', message.from_user.first_name)
    await message.answer(text, reply_markup=get_main_keyboard())
