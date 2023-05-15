from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_client_commands = ReplyKeyboardMarkup(resize_keyboard=True)
button_show_debts = KeyboardButton("Показать все долги")
button_send_to_teacher = KeyboardButton("Отправить сообщение куратору")
button_rename = KeyboardButton("Изменить имя")
kb_client_commands.add(button_show_debts).insert(button_send_to_teacher).insert(button_rename)

kb_confirmation = ReplyKeyboardMarkup(resize_keyboard=True)
button_confirm = KeyboardButton('Подтвердить')
button_decline = KeyboardButton('Отмена')
kb_confirmation.add(button_confirm, button_decline)