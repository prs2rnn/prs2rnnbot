from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from core.database import bot_db
from core.utils import load_html_content
from keyboards.user_keyboard import get_main_keyboard, get_proceed_feedback_keyboard
from states.state import FeedbackStates

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


@user_message_router.message(
    StateFilter(FeedbackStates.waiting_for_message), F.text == 'Отменить'
)
async def cancel_proceed_feedback(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Действие отменено', reply_markup=ReplyKeyboardRemove())
    text = load_html_content('start')
    await message.answer(text, reply_markup=get_main_keyboard())


@user_message_router.message(
    StateFilter(FeedbackStates.waiting_for_message),
)
async def handle_proceed_feedback(message: Message, state: FSMContext):
    user_message = message.text
    print(user_message)
    await message.answer(
        'Подтвердите или отмените отправку',
        reply_markup=get_proceed_feedback_keyboard(),
    )
    await state.clear()
    await state.set_state(FeedbackStates.waiting_for_confirmation)


@user_message_router.message(
    StateFilter(FeedbackStates.waiting_for_confirmation), F.text == 'Подтвердить'
)
async def confirm_feedback(message: Message, state: FSMContext):
    await message.answer(
        'Ваше сообщение успешно отправлено автору',
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.clear()
    text = load_html_content('start')
    await message.answer(text, reply_markup=get_main_keyboard())


@user_message_router.message(
    StateFilter(FeedbackStates.waiting_for_confirmation), F.text == 'Отменить'
)
async def cancel_confirm_feedback(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Действие отменено', reply_markup=ReplyKeyboardRemove())
    text = load_html_content('start')
    await message.answer(text, reply_markup=get_main_keyboard())


@user_message_router.message(StateFilter(FeedbackStates.waiting_for_confirmation))
async def handle_confirm_feedback(message: Message, state: FSMContext):
    user_message = message.text
    print(user_message)
    await message.answer(
        'Подтвердите или отмените отправку',
        reply_markup=get_proceed_feedback_keyboard(),
    )
