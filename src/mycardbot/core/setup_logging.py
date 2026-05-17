import asyncio
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from aiogram import Bot
from core.config import setting


class TelegramHandler(logging.Handler):

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot
        self.chat_id = setting.channel_id

    def emit(self, record):
        log_entry = self.format(record)
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return

        loop.create_task(self.send_message(log_entry))

    async def send_message(self, text: str):
        try:
            await self.bot.send_message(self.chat_id, text=f'🚨 {text[:4000]}')
        except Exception:
            pass


def get_formatter():
    return logging.Formatter(
        '%(asctime)s | %(name)s | '
        '%(levelname)s | '
        '%(funcName)s:%(lineno)d | '
        '%(message)s'
    )


def setup_logger(debug: bool):
    base_log_level = logging.INFO
    console_log_level = logging.WARNING
    file_log_level = logging.INFO
    if debug:
        base_log_level = logging.DEBUG
        console_log_level = logging.DEBUG
        file_log_level = logging.DEBUG

    log_dir = Path('data')
    log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger()

    if logger.handlers:
        return logger

    logger.setLevel(base_log_level)

    formatter = get_formatter()

    # Handler for console, INFO only or higher
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_log_level)
    console_handler.setFormatter(formatter)

    # Handler for file with rotation
    file_handler = RotatingFileHandler(
        filename=log_dir / 'bot.log',
        maxBytes=10 * 1024**2,
        backupCount=5,
        encoding='utf-8',
    )
    file_handler.setLevel(file_log_level)
    file_handler.setFormatter(formatter)

    # disable loggers from libraries
    # logging.getLogger('aiogram').setLevel(logging.WARNING)
    # logging.getLogger('aiosqlite').setLevel(logging.WARNING)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def setup_telegram_logger(logger: logging.Logger, bot: Bot) -> None:
    telegram_handler = TelegramHandler(bot)
    telegram_handler.setLevel(logging.WARNING)
    telegram_handler.setFormatter(get_formatter())
    logger.addHandler(telegram_handler)
