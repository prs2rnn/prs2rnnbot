import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(debug: bool):
    base_log_level = logging.INFO
    console_log_level = logging.WARNING
    file_log_level = logging.INFO
    if debug:
        base_log_level = logging.DEBUG
        console_log_level = logging.DEBUG
        file_log_level = logging.DEBUG

    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(base_log_level)

    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s'
    )

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
