"""
ОБРАБОТКА КОМАНД КУРАТОРА
"""

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageTextIsEmpty

from create_bot import bot
from databases import users_db, debts_db
from keyboards import admin_kb

# Constants
STUDENT_LIST_EMPTY_MESSAGE = "Список студентов пуст"
SELECT_STUDENT_MESSAGE = "Введите номер студента, c которым хотите взаимодействовать"


# States
class AdminStates(StatesGroup):
    student_number = State()
    student_commands = State()
    message = State()
    student_delete = State()
    confirmation = State()
    #
    debt = State()
    debt_delete_number = State()
    debt_edit_number = State()
    debt_add_number = State()
    debts_commands = State()
    debt_confirm_delete = State()
    debt_edit_text = State()
    debt_add_text = State()
    agree_add_debt = State()


"""
ВЫБОР СТУДЕНТА ИЗ СПИСКА
"""


# Вывод списка студентов
async def show_students(message: types.Message):
    try:
        users_id = message.from_user.id
        student_list = await users_db.get_list_students(users_id)
        if not student_list:
            await bot.send_message(chat_id=users_id, text=STUDENT_LIST_EMPTY_MESSAGE)
            return

        formatted_list = "\n".join([f"{i}. {item[0]}" for i, item in enumerate(student_list, start=1)])
        formatted_list = f"{formatted_list}"
        await bot.send_message(chat_id=users_id, text=formatted_list, parse_mode="HTML")
        await bot.send_message(chat_id=users_id, text=SELECT_STUDENT_MESSAGE)
        await AdminStates.student_number.set()
    except MessageTextIsEmpty:
        await bot.send_message(chat_id=message.from_user.id, text=STUDENT_LIST_EMPTY_MESSAGE)


# Выбор студента по номеру
async def select_student_number(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['student_id'] = await users_db.get_student_of_number(message.from_user.id, message.text)
        await bot.send_message(chat_id=message.from_user.id, text='Выберите действие',
                               reply_markup=admin_kb.kb_admin_commands)
        await AdminStates.student_commands.set()
    except (IndexError, ValueError) as e:
        await bot.send_message(chat_id=message.from_user.id, text="Введите корректное значение")


"""
ОТПРАВЛЕНИЕ СООБЩЕНИЯ СТУДЕНТУ
"""


# Начало отправки сообщения
async def writing_message_to_student(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id, text='Теперь наберите сообщение для студента')
    await AdminStates.message.set()


# Потдверждение отправки сообщения
async def confirmation_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['message'] = message.text
    await bot.send_message(chat_id=message.from_user.id, text='Уверены ли вы, что хотите отправить сообщение?',
                           reply_markup=admin_kb.kb_confirmation)
    await AdminStates.confirmation.set()


# Отправка сообщения
async def send_message_to_student(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        student_id = data['student_id']
        message_text = data['message']
        await bot.send_message(chat_id=student_id, text=f"<b>Сообщение от преподавателя:</b>\n{message_text}",
                               parse_mode="HTML")
    await bot.send_message(chat_id=message.from_user.id, text="Сообщение успешно отправлено",
                           reply_markup=admin_kb.kb_admin_commands)
    await AdminStates.student_commands.set()


"""
УДАЛЕНИЕ СТУДЕНТА
"""


async def confirmation_delete_student(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id, text='Уверены ли вы, что хотите удалить студента?',
                           reply_markup=admin_kb.kb_confirmation)
    await AdminStates.student_delete.set()


async def delete_student(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        student_id = data['student_id']
        await users_db.delete_student(student_id)
        await debts_db.delete_student(student_id, message.from_user.id)
    await bot.send_message(chat_id=message.from_user.id, text="Студент успешно удален",
                           reply_markup=admin_kb.kb_select_student)
    await state.finish()


"""
РАБОТА С ЗАДОЛЖНОСТЯМИ
"""


async def show_debts_student(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            student_id = data['student_id']
            await bot.send_message(chat_id=message.from_user.id,
                                   text=await debts_db.get_not_null_debts_student_text(message.from_user.id,
                                                                                       student_id),
                                   parse_mode="HTML", reply_markup=admin_kb.kb_debts)
            await AdminStates.debts_commands.set()
    except MessageTextIsEmpty:
        await bot.send_message(chat_id=message.from_user.id, text="Задолженностей не найдено, желаете добавить?",
                               reply_markup=admin_kb.kb_yes_or_no)
        await AdminStates.agree_add_debt.set()


# Подтверждение на добавление задолженности, когда их нет
async def agree_add_debt(message: types.Message):
    if message.text == 'Да':
        await add_debt_start(message)
    else:
        await bot.send_message(chat_id=message.from_user.id, text='Выберите действие',
                               reply_markup=admin_kb.kb_admin_commands)
        await AdminStates.student_commands.set()


async def delete_debt_start(message: types.Message):
    await message.delete()
    await bot.send_message(chat_id=message.from_user.id, text="Введите номер задолженности, который хотите удалить")
    await AdminStates.debt_delete_number.set()


async def select_debt_number_delete(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['name_debt'] = await debts_db.get_not_null_debt_of_number(message.from_user.id, data['student_id'],
                                                                           message.text)
            print(data['name_debt'])
        await bot.send_message(chat_id=message.from_user.id, text="Вы действительно хотите удалить задолженность?",
                               reply_markup=admin_kb.kb_confirmation)
        await AdminStates.debt_confirm_delete.set()
    except (IndexError, ValueError) as e:
        await bot.send_message(chat_id=message.from_user.id, text="Введите корректное значение")


async def confirm_delete_debt(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await debts_db.delete_debt_of_name(data['name_debt'], message.from_user.id, data['student_id'])
    await bot.send_message(chat_id=message.from_user.id, text='Долг был успешно удален',
                           reply_markup=admin_kb.kb_admin_commands)
    await AdminStates.student_commands.set()


async def back_to_student_commands(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id, text="Вы вернулись назад",
                           reply_markup=admin_kb.kb_admin_commands)
    await AdminStates.student_commands.set()


async def edit_debt_start(message: types.Message):
    await message.delete()
    await bot.send_message(chat_id=message.from_user.id, text="Введите номер задолженности, которую хотите изменить")
    await AdminStates.debt_edit_number.set()


async def select_debt_number_edit(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['name_debt'] = await debts_db.get_not_null_debt_of_number(message.from_user.id, data['student_id'],
                                                                           message.text)
        await bot.send_message(chat_id=message.from_user.id, text="Введите новый текст для задолженности")
        await AdminStates.debt_edit_text.set()
    except (IndexError, ValueError) as e:
        await bot.send_message(chat_id=message.from_user.id, text="Введите корректное значение")


async def edit_debt_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await debts_db.update_debt_of_name(data['name_debt'], message.from_user.id, data['student_id'], message.text)
    await bot.send_message(chat_id=message.from_user.id, text="Задолженность успешно обновлена",
                           reply_markup=admin_kb.kb_admin_commands)
    await AdminStates.student_commands.set()


async def add_debt_start(message: types.Message):
    await message.delete()
    await bot.send_message(chat_id=message.from_user.id,
                           text=await debts_db.get_all_debts_student_text(message.from_user.id))
    await bot.send_message(chat_id=message.from_user.id, text="Введите номер задолженности, которую хотите добавить")
    await AdminStates.debt_add_number.set()


async def select_debt_number_add(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['name_debt'] = await debts_db.get_all_debt_of_number(message.from_user.id, data['student_id'],
                                                                      message.text)
        await bot.send_message(chat_id=message.from_user.id, text="Введите текст для добавления задолженности")
        await AdminStates.debt_add_text.set()
    except (IndexError, ValueError) as e:
        await bot.send_message(chat_id=message.from_user.id, text="Введите корректное значение")


async def add_debt_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await debts_db.add_debt_of_name(data['name_debt'], message.from_user.id, data['student_id'], message.text)
    await bot.send_message(chat_id=message.from_user.id, text="Задолженность успешно обновлена",
                           reply_markup=admin_kb.kb_admin_commands)
    await AdminStates.student_commands.set()


"""
ПРОЧЕЕ
"""


async def back_command(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['student_id'] = None
    await bot.send_message(chat_id=message.from_user.id, text="Вы вернулись назад",
                           reply_markup=admin_kb.kb_select_student)
    await state.finish()


async def cancel_action(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id, text="Действие отменено",
                           reply_markup=admin_kb.kb_admin_commands)
    await AdminStates.student_commands.set()


def register_handlers_admin(dp: Dispatcher):
    # хендлеры выбора студента
    dp.register_message_handler(show_students, text="Выбрать студента", state="*")
    dp.register_message_handler(select_student_number, state=AdminStates.student_number)

    # хендлеры отправки сообщения
    dp.register_message_handler(writing_message_to_student, text="Отправить сообщение",
                                state=AdminStates.student_commands)
    dp.register_message_handler(confirmation_message, state=AdminStates.message)
    dp.register_message_handler(send_message_to_student, text="Подтвердить", state=AdminStates.confirmation)

    # хендлеры удаления студента
    dp.register_message_handler(confirmation_delete_student, text="Удалить", state=AdminStates.student_commands)
    dp.register_message_handler(delete_student, text="Подтвердить", state=AdminStates.student_delete)

    # хендлеры работы с долгами
    dp.register_message_handler(show_debts_student, text='Задолженности', state=AdminStates.student_commands)
    dp.register_message_handler(delete_debt_start, text='Удалить задолженность', state=AdminStates.debts_commands)
    dp.register_message_handler(select_debt_number_delete, state=AdminStates.debt_delete_number)
    dp.register_message_handler(confirm_delete_debt, text='Подтвердить', state=AdminStates.debt_confirm_delete)
    dp.register_message_handler(back_to_student_commands, text="Назад", state=AdminStates.debts_commands)
    dp.register_message_handler(edit_debt_start, text='Изменить задолженность', state=AdminStates.debts_commands)
    dp.register_message_handler(select_debt_number_edit, state=AdminStates.debt_edit_number)
    dp.register_message_handler(edit_debt_text, state=AdminStates.debt_edit_text)
    dp.register_message_handler(add_debt_start, text='Добавить задолженность', state=AdminStates.debts_commands)
    dp.register_message_handler(select_debt_number_add, state=AdminStates.debt_add_number)
    dp.register_message_handler(add_debt_text, state=AdminStates.debt_add_text)
    dp.register_message_handler(agree_add_debt, state=AdminStates.agree_add_debt)
    # прочее
    dp.register_message_handler(cancel_action, text="Отмена", state=AdminStates)
    dp.register_message_handler(back_command, text="Назад", state=AdminStates.student_commands)
