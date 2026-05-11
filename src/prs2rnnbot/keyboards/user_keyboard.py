from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='👤 Now', callback_data='now')
    builder.button(text='📝 CV', callback_data='cv')
    builder.button(text='📝 Связаться c автором', callback_data='feedback')
    builder.button(text='🌐 Сайт', url='https://prs2rnn.github.io/')
    builder.adjust(2)
    return builder.as_markup()


def get_return_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='🔙 Вернуться назад', callback_data='menu')
    return builder.as_markup()


def get_cancel_feedback_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text='Отменить')
    return builder.as_markup(resize_keyboard=True)


def get_proceed_feedback_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text='Подтвердить')
    builder.button(text='Отменить')
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)
