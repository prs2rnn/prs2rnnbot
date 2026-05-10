from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from utils import load_html_content

message_router = Router()


@message_router.message(CommandStart())
async def start(message: Message) -> None:
    text = load_html_content('start')
    await message.answer(text)
