from aiogram import F, Router
from aiogram.types import CallbackQuery
from core.database import bot_db
from core.utils import load_html_content
from filters.check_admin import IsAdmin
from keyboards.admin_keyboard import get_main_keyboard, get_return_keyboard

admin_callback_router = Router()


@admin_callback_router.callback_query(F.data == 'admin_list', IsAdmin())
async def list(callback: CallbackQuery) -> None:
    text = await bot_db.list_users()
    await callback.message.edit_text(text, reply_markup=get_return_keyboard())


@admin_callback_router.callback_query(F.data == 'admin_menu', IsAdmin())
async def menu(callback: CallbackQuery) -> None:
    text = load_html_content('admin')
    text = text.replace('{name}', callback.from_user.first_name)
    await callback.message.edit_text(text, reply_markup=get_main_keyboard())
