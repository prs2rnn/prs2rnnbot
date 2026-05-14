from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from core.database import bot_db
from core.utils import get_changelog, load_html_content
from keyboards.user_keyboard import (
    get_broadcast_keyboard,
    get_cancel_feedback_keyboard,
    get_cv_keyboard,
    get_main_feedback_keyboard,
    get_main_keyboard,
    get_return_feedback_keyboard,
    get_return_keyboard,
)
from states.user import FeedbackStates

user_callback_router = Router()


@user_callback_router.callback_query(F.data == 'now')
async def now(callback: CallbackQuery):
    text = load_html_content('now')
    await callback.message.edit_text(text, reply_markup=get_return_keyboard())
    await callback.answer()


@user_callback_router.callback_query(F.data == 'menu')
async def menu(callback: CallbackQuery):
    text = load_html_content('start')
    await callback.message.edit_text(text, reply_markup=get_main_keyboard())
    await callback.answer()


@user_callback_router.callback_query(F.data == 'feedback')
async def feedback(callback: CallbackQuery, state: FSMContext):
    text = load_html_content('feedback')
    await callback.message.edit_text(text, reply_markup=get_main_feedback_keyboard())
    await callback.answer()


@user_callback_router.callback_query(F.data == 'send')
async def proceed_feedback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        'Напишите ваше сообщение', reply_markup=get_cancel_feedback_keyboard()
    )
    await state.set_state(FeedbackStates.waiting_for_message)
    await callback.answer()


@user_callback_router.callback_query(F.data == 'contact')
async def contact(callback: CallbackQuery):
    text = load_html_content('contact')
    await callback.message.edit_text(text, reply_markup=get_return_feedback_keyboard())
    await callback.answer()


@user_callback_router.callback_query(F.data == 'cv')
async def cv(callback: CallbackQuery):
    text = load_html_content('cv')
    await callback.message.edit_text(text, reply_markup=get_cv_keyboard())
    await callback.answer()


@user_callback_router.callback_query(F.data == 'broadcast')
async def broadcast(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_subscribed = await bot_db.is_subscribed(user_id)
    text = load_html_content('broadcast')
    await callback.message.edit_text(
        text, reply_markup=get_broadcast_keyboard(is_subscribed)
    )
    await callback.answer()


@user_callback_router.callback_query(F.data == 'unsubscribe')
@user_callback_router.callback_query(F.data == 'subscribe')
async def proceed_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_subscribed = await bot_db.is_subscribed(user_id)

    if is_subscribed is None:
        await bot_db.add_user(
            callback.from_user.full_name, callback.from_user.username, user_id
        )

    await (
        bot_db.subscribe(user_id) if not is_subscribed else bot_db.unsubscribe(user_id)
    )

    await callback.message.edit_reply_markup(
        reply_markup=get_broadcast_keyboard(not is_subscribed)
    )

    await callback.answer(
        'Вы подписались на рассылку!'
        if not is_subscribed
        else 'Вы отписались от рассылки!'
    )


@user_callback_router.callback_query(F.data == 'changelog')
async def changelog(callback: CallbackQuery):
    releases = await get_changelog()
    text = 'Последние обновления:\n\n'
    if not releases:
        text += 'Не удалось получить информацию от сервера'
    else:
        for r in releases:
            text += f'*{r['version']}*\n{r['text']}\n\n'

    await callback.message.edit_text(
        text, reply_markup=get_return_keyboard(), parse_mode='Markdown'
    )
