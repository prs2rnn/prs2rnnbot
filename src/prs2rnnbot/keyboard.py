from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='👤 Now', callback_data='now')
    builder.button(text='📝 CV', callback_data='cv')
    builder.button(text='📧 Связаться c автором', callback_data='feedback')
    builder.button(text='🌐 Блог', url='https://prs2rnn.github.io/')
    builder.adjust(2)
    return builder.as_markup()
