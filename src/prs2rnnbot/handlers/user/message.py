from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from keyboard import get_main_keyboard
from utils import load_html_content

message_router = Router()


@message_router.message(CommandStart())
async def start(message: Message) -> None:
    text = load_html_content('start', message.from_user.first_name)
    await message.answer(text, reply_markup=get_main_keyboard())
