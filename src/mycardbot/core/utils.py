import asyncio
import logging
import random
import time
from pathlib import Path

import httpx
from aiogram import Bot
from aiogram.types import Message, ReplyKeyboardRemove, User
from core.config import setting

CACHE = {'data': None, 'updated_at': 0}
CACHE_TTL = 60 * 10


def load_html_content(section: str) -> str:
    file_path = Path(__file__).parent.parent / f'content/{section}.html'
    text = file_path.read_text(encoding='utf-8')
    return text if file_path.exists() else ''


async def fetch_json(url: str):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except (httpx.TimeoutException, httpx.HTTPStatusError, httpx.RequestError) as e:
        logging.error(f'Error occurred in fetch_json: {e}')
    except Exception as e:
        logging.error(f'Unexpected error occurred in fetch_json: {e}')


async def get_changelog():
    now = time.perf_counter()

    if CACHE['data'] and now - CACHE['updated_at'] < CACHE_TTL:
        logging.info('Retrieve changelog data from cache')
        return CACHE['data']

    url = 'https://api.github.com/repos/prs2rnn/mycardbot/releases'

    data = await fetch_json(url)

    if not data:
        return []

    result = [
        {'version': r.get('name', 'unknown'), 'text': r.get('body', '')} for r in data
    ][0]

    CACHE['data'] = result
    CACHE['updated_at'] = now

    return result


async def extract_content_from_message(message: Message) -> tuple[dict, str]:
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
    elif message.video_note:
        content_type = 'video_note'
        content_data['video_note_file_id'] = message.video_note.file_id
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

    return content_data, content_type


async def send_message(bot: Bot, user: User, content_type: str, content_data: dict):
    header = (
        f'👤 Новое сообщение от пользователя:\n\n'
        f'Имя: {user.full_name}\n'
        f'username: @{user.username}\n'
        f'ID: {user.id}\n\n'
    )

    send_methods = {
        'photo': lambda: bot.send_photo(
            setting.channel_id,
            photo=content_data['photo_file_id'],
            caption=f'{header}{content_data["caption"]}',
        ),
        'document': lambda: bot.send_document(
            setting.channel_id,
            document=content_data['document_file_id'],
            caption=f'{header}{content_data["caption"]}',
        ),
        'video': lambda: bot.send_video(
            setting.channel_id,
            video=content_data['video_file_id'],
            caption=f'{header}{content_data["caption"]}',
        ),
        'video_note': lambda: bot.send_video_note(
            setting.channel_id,
            video_note=content_data['video_note_file_id'],
        ),
        'voice': lambda: bot.send_voice(
            setting.channel_id,
            voice=content_data['voice_file_id'],
            caption=f'{header}{content_data["caption"]}',
        ),
        'audio': lambda: bot.send_audio(
            setting.channel_id,
            audio=content_data['audio_file_id'],
            caption=f'{header}{content_data["caption"]}',
            title=content_data.get('title'),
            performer=content_data.get('performer'),
        ),
        'text': lambda: bot.send_message(
            setting.channel_id, text=f'{header}Текст:\n{content_data["text"]}'
        ),
    }
    try:
        await send_methods.get(content_type)()
        await bot.send_message(
            user.id,
            'Ваше сообщение успешно отправлено',
            reply_markup=ReplyKeyboardRemove(),
        )
    except Exception as e:
        logging.error(e)
        await bot.send_message(
            user.id,
            'Произошла ошибка при отправке сообщения',
            reply_markup=ReplyKeyboardRemove(),
        )


async def send_broadcast(
    bot: Bot, admin: User, users: list[Users], content_type: str, content_data: dict
):
    header = f'📢 Новая рассылка от бота:\n\n'

    send_methods = {
        'photo': lambda user_id: bot.send_photo(
            user_id,
            photo=content_data['photo_file_id'],
            caption=f'{header}{content_data["caption"]}',
        ),
        'document': lambda user_id: bot.send_document(
            user_id,
            document=content_data['document_file_id'],
            caption=f'{header}{content_data["caption"]}',
        ),
        'video': lambda user_id: bot.send_video(
            user_id,
            video=content_data['video_file_id'],
            caption=f'{header}{content_data["caption"]}',
        ),
        'video_note': lambda user_id: bot.send_video_note(
            user_id,
            video_note=content_data['video_note_file_id'],
        ),
        'voice': lambda user_id: bot.send_voice(
            user_id,
            voice=content_data['voice_file_id'],
            caption=f'{header}{content_data["caption"]}',
        ),
        'audio': lambda user_id: bot.send_audio(
            user_id,
            audio=content_data['audio_file_id'],
            caption=f'{header}{content_data["caption"]}',
            title=content_data.get('title'),
            performer=content_data.get('performer'),
        ),
        'text': lambda user_id: bot.send_message(
            user_id, text=f'{header}Текст:\n{content_data["text"]}'
        ),
    }
    success, failure = 0, 0
    await bot.send_message(
        admin.id, 'Начинаю рассылку...', reply_markup=ReplyKeyboardRemove()
    )
    if not users:
        await bot.send_message(
            admin.id,
            'Нет пользователей, подписавшихся на рассылку. Действие отменено',
        )
        return
    try:
        for user in users:
            try:
                await send_methods.get(content_type)(str(user))
                success += 1
                pause = random.uniform(0.8, 1.8)
                await asyncio.sleep(pause)
            except Exception as e:
                failure += 1
                logging.error(f'Error: {e}, ID: {user}')
        await bot.send_message(
            admin.id,
            f'Ваше сообщение для рассылки отправлено\n\n'
            f'Успешно: {success}\n'
            f'Неудачно: {failure}',
        )
    except Exception as e:
        logging.error(e)
        await bot.send_message(admin.id, 'Произошла ошибка при отправке рассылки')

    # archive to channel
    await send_methods.get(content_type)(setting.channel_id)
