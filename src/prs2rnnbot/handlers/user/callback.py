from aiogram import F, Router
from aiogram.types import CallbackQuery

callback_router = Router()


@callback_router.callback_query(F.data == 'feedback')
@callback_router.callback_query(F.data == 'cv')
@callback_router.callback_query(F.data == 'now')
async def in_progress(callback: CallbackQuery):
    return callback.answer('Этот раздел находится в разработке!')
