import html

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from core.database import bot_db
from core.utils import load_html_content
from filters.check_admin import IsAdmin
from keyboards.admin_keyboard import (
    get_cancel_broadcast_keyboard,
    get_main_keyboard,
    get_return_keyboard,
)
from states.admin import BroadcastStates

admin_callback_router = Router()


@admin_callback_router.callback_query(F.data == 'admin_list', IsAdmin())
async def list(callback: CallbackQuery) -> None:
    text = await bot_db.list_users()
    await callback.message.edit_text(text, reply_markup=get_return_keyboard())
    await callback.answer()


@admin_callback_router.callback_query(F.data == 'admin_menu', IsAdmin())
async def menu(callback: CallbackQuery) -> None:
    text = load_html_content('admin')
    text = text.replace('{name}', html.escape(callback.from_user.first_name))
    await callback.message.edit_text(text, reply_markup=get_main_keyboard())
    await callback.answer()


@admin_callback_router.callback_query(F.data == 'admin_broadcast', IsAdmin())
async def proceed_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    text = load_html_content('admin_broadcast')
    await callback.message.answer(text, reply_markup=get_cancel_broadcast_keyboard())
    await state.set_state(BroadcastStates.waiting_for_message)
    await callback.answer()
