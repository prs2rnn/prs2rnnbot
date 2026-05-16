import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from core.config import setting
from core.setup_logging import setup_logger
from core.setup_routers import setup_router
from middlewares.logging import LoggingMiddleware
from middlewares.notification import NewUserNotificationMiddleware


async def main():
    logger = setup_logger(setting.debug)
    bot = None
    try:
        bot = Bot(setting.bot_token, default=DefaultBotProperties(parse_mode='HTML'))
        dp = Dispatcher()
        router = setup_router()
        dp.include_router(router)
        dp.update.outer_middleware(LoggingMiddleware(logger))
        dp.update.outer_middleware(NewUserNotificationMiddleware(bot))
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f'Critical error: {e}', exc_info=True)
    finally:
        if bot:
            await bot.session.close()
        logger.info('Bot stopped gracefully!')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error('Bot stopped manually!')
