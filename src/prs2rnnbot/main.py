import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from core.config import BOT_TOKEN
from core.setup_logging import setup_logger
from core.setup_routers import setup_router
from middlewares.logging import LoggingMiddleware


async def main():
    logger = setup_logger()
    try:
        bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
        dp = Dispatcher()
        router = setup_router()
        dp.include_router(router)
        dp.update.outer_middleware(LoggingMiddleware(logger))
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f'Critical error: {e}', exc_info=True)
    finally:
        await bot.session.close()
        logger.info('Bot stopped gracefully!')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error('Bot stopped manually!')
