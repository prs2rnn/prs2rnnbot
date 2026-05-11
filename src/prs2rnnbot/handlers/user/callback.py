from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from core.utils import load_html_content
from keyboards.user_keyboard import (
    get_cancel_feedback_keyboard,
    get_main_keyboard,
    get_return_keyboard,
)
from states.state import FeedbackStates

user_callback_router = Router()


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


@user_callback_router.callback_query(F.data == 'feedback')
async def feedback(callback: CallbackQuery, state: FSMContext):
    # await callback.message.delete()
    await callback.message.answer(
        'Отправьте ваше сообщение автору', reply_markup=get_cancel_feedback_keyboard()
    )
    await state.set_state(FeedbackStates.waiting_for_message)
    await callback.answer()
