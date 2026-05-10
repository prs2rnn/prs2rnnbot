import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN
from handlers.user.message import message_router


async def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
    )
    try:
        bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
        dp = Dispatcher()
        dp.include_routers(message_router)
        await dp.start_polling(bot)
    except Exception as e:
        logging.critical(f'Critical error: {e}', exc_info=True)
    finally:
        await bot.session.close()
        logging.info('Bot stopped gracefully!')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error('Bot stopped manually!')
