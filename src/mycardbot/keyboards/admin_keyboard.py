from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='🏠 Главная', callback_data='menu')
    builder.button(text='👥 Список пользователей', callback_data='admin_list')
    builder.button(text='📨 Создать рассылку', callback_data='admin_broadcast')
    builder.adjust(1)
    return builder.as_markup()


def get_return_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='🔙 Вернуться назад', callback_data='admin_menu')
    return builder.as_markup()


def get_cancel_broadcast_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text='Отменить')
    return builder.as_markup(resize_keyboard=True)


def get_proceed_broadcast_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text='Подтвердить')
    builder.button(text='Отменить')
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)
