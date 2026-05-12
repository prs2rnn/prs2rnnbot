import asyncio
import logging
import random

from aiogram import Bot, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from core.database import bot_db
from core.utils import load_html_content
from filters.check_admin import IsAdmin
from keyboards.admin_keyboard import get_main_keyboard, get_proceed_broadcast_keyboard
from states.admin import BroadcastStates

admin_message_router = Router()


@admin_message_router.message(Command('admin'), IsAdmin())
async def list(message: Message) -> None:
    text = load_html_content('admin')
    text = text.replace('{name}', message.from_user.first_name)
    await message.answer(text, reply_markup=get_main_keyboard())


@admin_message_router.message(
    StateFilter(BroadcastStates.waiting_for_message), F.text == 'Отменить'
)
async def cancel_broadcast(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Действие отменено', reply_markup=ReplyKeyboardRemove())
    text = load_html_content('admin')
    text = text.replace('{name}', message.from_user.first_name)
    await message.answer(text, reply_markup=get_main_keyboard())


@admin_message_router.message(StateFilter(BroadcastStates.waiting_for_message))
async def handle_broadcast(message: Message, state: FSMContext):
    content_data = {}
    content_type = None

    if message.photo:
        content_type = 'photo'
        content_data['caption'] = message.caption or ''
        content_data['photo_file_id'] = message.photo[-1].file_id
    elif message.document:
        content_type = 'document'
        content_data['caption'] = message.caption or ''
        content_data['document_file_id'] = message.document.file_id
        content_data['file_name'] = message.document.file_name
    elif message.video:
        content_type = 'video'
        content_data['caption'] = message.caption or ''
        content_data['video_file_id'] = message.video.file_id
    elif message.voice:
        content_type = 'voice'
        content_data['caption'] = message.caption or 'Голосовое сообщение'
        content_data['voice_file_id'] = message.voice.file_id
        content_data['duration'] = message.voice.duration
    elif message.audio:
        content_type = 'audio'
        content_data['caption'] = (
            message.caption or f"Аудио: {message.audio.title or ''}"
        )
        content_data['audio_file_id'] = message.audio.file_id
        content_data['title'] = message.audio.title
        content_data['performer'] = message.audio.performer
    elif message.video_note:
        content_type = 'video_note'
        content_data['video_note_file_id'] = message.video_note.file_id
    elif message.text:
        content_type = 'text'
        content_data['text'] = message.text
    else:
        await message.answer('Этот тип сообщения не поддерживается')
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
    send_methods = {
        'photo': lambda user_id: bot.send_photo(
            user_id,
            photo=content_data['photo_file_id'],
            caption=content_data['caption'],
        ),
        'document': lambda user_id: bot.send_document(
            user_id,
            document=content_data['document_file_id'],
            caption=content_data['caption'],
        ),
        'video': lambda user_id: bot.send_video(
            user_id,
            video=content_data['video_file_id'],
            caption=content_data['caption'],
        ),
        'voice': lambda user_id: bot.send_voice(
            user_id,
            voice=content_data['voice_file_id'],
            caption=content_data['caption'],
        ),
        'audio': lambda user_id: bot.send_audio(
            user_id,
            audio=content_data['audio_file_id'],
            caption=content_data['caption'],
            title=content_data.get('title'),
            performer=content_data.get('performer'),
        ),
        'video_note': lambda user_id: bot.send_video_note(
            user_id,
            video_note=content_data['video_note_file_id'],
        ),
        'text': lambda user_id: bot.send_message(user_id, text=content_data['text']),
    }
    success, failure = 0, 0
    await message.answer('Начинаю рассылку...', reply_markup=ReplyKeyboardRemove())
    try:
        for user in users:
            try:
                await (send_methods.get(content_type) or send_methods('text'))(
                    str(user)
                )
                success += 1
                pause = random.uniform(0.8, 1.8)
                await asyncio.sleep(pause)
            except Exception as e:
                failure += 1
                logging.error(f'Error: {e}, ID: {user}')
        await message.answer(
            f'Ваше сообщение для рассылки отправлено\n\n'
            f'Успешно: {success}\n'
            f'Неудачно: {failure}',
        )
    except TypeError as e:
        logging.error(e)
        await message.answer(
            'Нет пользователей, подписавшихся на рассылку. Действие отменено',
        )
    except Exception as e:
        logging.error(e)
        await message.answer('Произошла ошибка при отправке рассылки')
    await state.clear()
    text = load_html_content('admin')
    text = text.replace('{name}', message.from_user.first_name)
    await message.answer(text, reply_markup=get_main_keyboard())


@admin_message_router.message(
    StateFilter(BroadcastStates.waiting_for_confirmation), F.text == 'Отменить'
)
async def cancel_confirm_broadcast(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Действие отменено', reply_markup=ReplyKeyboardRemove())
    text = load_html_content('admin')
    text = text.replace('{name}', message.from_user.first_name)
    await message.answer(text, reply_markup=get_main_keyboard())


@admin_message_router.message(StateFilter(BroadcastStates.waiting_for_confirmation))
async def handle_confirm_broadcast(message: Message, state: FSMContext):
    await message.answer(
        'Подтвердите или отмените отправку',
        reply_markup=get_proceed_broadcast_keyboard(),
    )
