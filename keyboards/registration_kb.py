from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def select_role() -> InlineKeyboardMarkup:
    ikb_reg = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Куратор', callback_data='teacher')],
        [InlineKeyboardButton('Студент', callback_data='student')]
    ])
    return ikb_reg
