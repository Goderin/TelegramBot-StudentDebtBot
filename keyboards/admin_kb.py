from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_select_student = ReplyKeyboardMarkup(resize_keyboard=True)
button_select_student = KeyboardButton('Выбрать студента')
kb_select_student.add(button_select_student)

kb_admin_commands = ReplyKeyboardMarkup(resize_keyboard=True)
button_back = KeyboardButton('Назад')
button_send_message = KeyboardButton('Отправить сообщение')
button_delete_student = KeyboardButton('Удалить')
button_debts = KeyboardButton('Задолженности')
kb_admin_commands.insert(button_back).add(button_delete_student).insert(button_debts).add(button_send_message)

kb_debts = ReplyKeyboardMarkup(resize_keyboard=True)
button_add_debt = KeyboardButton('Добавить задолженность')
button_delete_debt = KeyboardButton('Удалить задолженность')
button_edit_debt = KeyboardButton('Изменить задолженность')
kb_debts.insert(button_add_debt).insert(button_delete_debt).insert(button_edit_debt).insert(button_back)

kb_confirmation = ReplyKeyboardMarkup(resize_keyboard=True)
button_confirm = KeyboardButton('Подтвердить')
button_decline = KeyboardButton('Отмена')
kb_confirmation.add(button_confirm, button_decline)

kb_yes_or_no = ReplyKeyboardMarkup(resize_keyboard=True)
button_yes = KeyboardButton('Да')
button_no = KeyboardButton('Нет')
kb_yes_or_no.add(button_yes, button_no)