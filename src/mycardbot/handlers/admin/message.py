import asyncio
import html
import logging

from aiogram import Bot, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from core.config import setting
from core.database import bot_db
from core.utils import extract_content_from_message, load_html_content, send_broadcast
from filters.check_admin import IsAdmin
from keyboards.admin_keyboard import get_main_keyboard, get_proceed_broadcast_keyboard
from states.admin import BroadcastStates

admin_message_router = Router()


@admin_message_router.message(Command('admin'), IsAdmin())
async def list(message: Message) -> None:
    text = load_html_content('admin')
    text = text.replace('{name}', html.escape(message.from_user.first_name))
    await message.answer(text, reply_markup=get_main_keyboard())


@admin_message_router.message(
    StateFilter(BroadcastStates.waiting_for_message), F.text == 'Отменить'
)
async def cancel_broadcast(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Действие отменено', reply_markup=ReplyKeyboardRemove())
    text = load_html_content('admin')
    text = text.replace('{name}', html.escape(message.from_user.first_name))
    await message.answer(text, reply_markup=get_main_keyboard())


@admin_message_router.message(StateFilter(BroadcastStates.waiting_for_message))
async def handle_broadcast(message: Message, state: FSMContext):
    content_data, content_type = await extract_content_from_message(message)
    if not content_data or not content_type:
        return

    await state.update_data(pending_content=content_data, content_type=content_type)

    await message.answer(
        'Подтвердите или отмените отправку',
        reply_markup=get_proceed_broadcast_keyboard(),
    )
    await state.set_state(state=None)
    await state.set_state(BroadcastStates.waiting_for_confirmation)


@admin_message_router.message(
    StateFilter(BroadcastStates.waiting_for_confirmation), F.text == 'Подтвердить'
)
async def confirm_broadcast(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    content_data = data.get('pending_content', {})
    content_type = data.get('content_type')
    users = await bot_db.get_subscribed_users()
    admin = message.from_user

    await send_broadcast(bot, admin, users, content_type, content_data)

    await state.clear()
    text = load_html_content('admin')
    text = text.replace('{name}', html.escape(admin.first_name))
    await message.answer(text, reply_markup=get_main_keyboard())


@admin_message_router.message(
    StateFilter(BroadcastStates.waiting_for_confirmation), F.text == 'Отменить'
)
async def cancel_confirm_broadcast(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Действие отменено', reply_markup=ReplyKeyboardRemove())
    text = load_html_content('admin')
    text = text.replace('{name}', html.escape(message.from_user.first_name))
    await message.answer(text, reply_markup=get_main_keyboard())


@admin_message_router.message(StateFilter(BroadcastStates.waiting_for_confirmation))
async def handle_confirm_broadcast(message: Message, state: FSMContext):
    await message.answer(
        'Подтвердите или отмените отправку',
        reply_markup=get_proceed_broadcast_keyboard(),
    )


@admin_message_router.message(F.chat.id == setting.group_id, F.reply_to_message)
async def reply(message: Message, bot: Bot):
    reply_message_id = message.reply_to_message.message_id
    user_id = await bot_db.get_user_id_by_group_message_id(reply_message_id)
    try:
        await bot.send_message(
            user_id,
            text=f'💬 Ответ на сообщение #{reply_message_id}:\n\n{message.text}',
        )
        await message.reply(f'Сообщение успешно отправлено пользователю!')
    except Exception as e:
        logging.error(e)
        await message.reply(f'Не удалось отправить сообщение пользователю')
