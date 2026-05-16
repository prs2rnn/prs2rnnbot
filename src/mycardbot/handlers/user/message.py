import logging

from aiogram import Bot, F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from core.config import setting
from core.database import bot_db
from core.utils import extract_content_from_message, load_html_content, send_message
from keyboards.user_keyboard import (
    get_main_feedback_keyboard,
    get_main_keyboard,
    get_proceed_feedback_keyboard,
)
from states.user import FeedbackStates

user_message_router = Router()


@user_message_router.message(CommandStart())
async def start(message: Message) -> None:
    text = load_html_content('start')
    await message.answer(text, reply_markup=get_main_keyboard())


@user_message_router.message(
    StateFilter(FeedbackStates.waiting_for_message), F.text == 'Отменить'
)
async def cancel_proceed_feedback(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Действие отменено', reply_markup=ReplyKeyboardRemove())
    text = load_html_content('feedback')
    await message.answer(text, reply_markup=get_main_feedback_keyboard())


@user_message_router.message(
    StateFilter(FeedbackStates.waiting_for_message),
)
async def handle_proceed_feedback(message: Message, state: FSMContext):
    content_data, content_type = await extract_content_from_message(message)
    if not content_data or not content_type:
        return

    await state.update_data(pending_content=content_data, content_type=content_type)

    await message.answer(
        'Подтвердите или отмените отправку',
        reply_markup=get_proceed_feedback_keyboard(),
    )
    await state.set_state(state=None)
    await state.set_state(FeedbackStates.waiting_for_confirmation)


@user_message_router.message(
    StateFilter(FeedbackStates.waiting_for_confirmation), F.text == 'Подтвердить'
)
async def confirm_feedback(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    content_data = data.get('pending_content', {})
    content_type = data.get('content_type')
    user = message.from_user

    await send_message(bot, user, content_type, content_data)

    await state.clear()
    text = load_html_content('start')
    await message.answer(text, reply_markup=get_main_keyboard())


@user_message_router.message(
    StateFilter(FeedbackStates.waiting_for_confirmation), F.text == 'Отменить'
)
async def cancel_confirm_feedback(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Действие отменено', reply_markup=ReplyKeyboardRemove())
    text = load_html_content('feedback')
    await message.answer(text, reply_markup=get_main_feedback_keyboard())


@user_message_router.message(StateFilter(FeedbackStates.waiting_for_confirmation))
async def handle_confirm_feedback(message: Message, state: FSMContext):
    await message.answer(
        'Подтвердите или отмените отправку',
        reply_markup=get_proceed_feedback_keyboard(),
    )
