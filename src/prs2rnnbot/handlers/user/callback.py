from aiogram import F, Router
from aiogram.types import CallbackQuery
from core.utils import load_html_content
from keyboards.user_keyboard import get_main_keyboard, get_return_keyboard

user_callback_router = Router()


@user_callback_router.callback_query(F.data == 'feedback')
@user_callback_router.callback_query(F.data == 'cv')
async def in_progress(callback: CallbackQuery):
    await callback.answer('Этот раздел находится в разработке!')


@user_callback_router.callback_query(F.data == 'now')
async def now(callback: CallbackQuery):
    text = load_html_content('now')
    await callback.message.edit_text(text, reply_markup=get_return_keyboard())


@user_callback_router.callback_query(F.data == 'menu')
async def menu(callback: CallbackQuery):
    text = load_html_content('start')
    await callback.message.edit_text(text, reply_markup=get_main_keyboard())
