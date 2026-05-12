import logging

from aiogram import Bot, F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from core.config import ADMIN_ID
from core.database import bot_db
from core.utils import load_html_content
from keyboards.user_keyboard import (
    get_main_feedback_keyboard,
    get_main_keyboard,
    get_proceed_feedback_keyboard,
)
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
    text = load_html_content('feedback')
    await message.answer(text, reply_markup=get_main_feedback_keyboard())


@user_message_router.message(
    StateFilter(FeedbackStates.waiting_for_message),
)
async def handle_proceed_feedback(message: Message, state: FSMContext):
    content_data = {}
    content_type = None

    if message.photo:
        content_type = 'photo'
        content_data['caption'] = message.caption or 'Фото без описания'
        content_data['photo_file_id'] = message.photo[-1].file_id
    elif message.document:
        content_type = 'document'
        content_data['caption'] = (
            message.caption or f"Документ: {message.document.file_name}"
        )
        content_data['document_file_id'] = message.document.file_id
        content_data['file_name'] = message.document.file_name
    elif message.video:
        content_type = 'video'
        content_data['caption'] = message.caption or "Видео без описания"
        content_data['video_file_id'] = message.video.file_id
    elif message.voice:
        content_type = 'voice'
        content_data['caption'] = message.caption or "Голосовое сообщение"
        content_data['voice_file_id'] = message.voice.file_id
        content_data['duration'] = message.voice.duration
    elif message.audio:
        content_type = 'audio'
        content_data['caption'] = (
            message.caption or f"Аудио: {message.audio.title or 'Без названия'}"
        )
        content_data['audio_file_id'] = message.audio.file_id
        content_data['title'] = message.audio.title
        content_data['performer'] = message.audio.performer
    elif message.text:
        content_type = 'text'
        content_data['text'] = message.text
    else:
        await message.answer('Этот тип сообщения не поддерживается')
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
    try:
        header = (
            f'📩 Новое сообщение от пользователя:\n\n'
            f'Имя: {user.full_name}\n'
            f'username: @{user.username or 'нет'}\n'
            f'ID: {user.id}\n\n'
        )

        send_methods = {
            'photo': lambda: bot.send_photo(
                ADMIN_ID,
                photo=content_data['photo_file_id'],
                caption=f'{header}{content_data["caption"]}',
            ),
            'document': lambda: bot.send_document(
                ADMIN_ID,
                document=content_data['document_file_id'],
                caption=f'{header}{content_data["caption"]}',
            ),
            'video': lambda: bot.send_video(
                ADMIN_ID,
                video=content_data['video_file_id'],
                caption=f'{header}{content_data["caption"]}',
            ),
            'voice': lambda: bot.send_voice(
                ADMIN_ID,
                voice=content_data['voice_file_id'],
                caption=f'{header}{content_data["caption"]}',
            ),
            'audio': lambda: bot.send_audio(
                ADMIN_ID,
                audio=content_data['audio_file_id'],
                caption=f'{header}{content_data["caption"]}',
                title=content_data.get('title'),
                performer=content_data.get('performer'),
            ),
            'text': lambda: bot.send_message(
                ADMIN_ID, text=f'{header}📝 Текст:\n{content_data["text"]}'
            ),
        }
        await (send_methods.get(content_type) or send_methods['text'])()
        await message.answer(
            'Ваше сообщение успешно отправлено',
            reply_markup=ReplyKeyboardRemove(),
        )
    except Exception as e:
        logging.error(e)
        await message.answer('Произошла ошибка при отправке сообщения')

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
    user_message = message.text
    await message.answer(
        'Подтвердите или отмените отправку',
        reply_markup=get_proceed_feedback_keyboard(),
    )
