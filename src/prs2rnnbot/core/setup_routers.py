from aiogram import Router
from handlers.admin.callback import admin_callback_router
from handlers.admin.message import admin_message_router
from handlers.user.callback import user_callback_router
from handlers.user.message import user_message_router


def setup_routers() -> Router:
    router = Router()
    router.include_routers(
        admin_message_router,
        admin_callback_router,
        user_message_router,
        user_callback_router,
    )
    return router
