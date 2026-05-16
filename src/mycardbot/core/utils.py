import asyncio
import logging
import time
from pathlib import Path

import httpx
from aiogram import Bot
from aiogram.types import ReplyKeyboardRemove, User
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


async def send_message(bot: Bot, user: User, content_type: str, content_data: dict):
    header = (
        f'📩 Новое сообщение от пользователя:\n\n'
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
