from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageTextIsEmpty

from create_bot import bot
from databases import users_db, debts_db
from keyboards import client_kb


class ClientStates(StatesGroup):
    commands = State()
    message = State()
    rename = State()
    confirmation_message = State()
    confirmation_rename = State()


async def show_all_debts(message: types.Message):
    try:
        await bot.send_message(chat_id=message.from_user.id,
                               text=await debts_db.get_not_null_debts_student_text(message.from_user.id,
                                                                                   message.from_user.id),
                               parse_mode="HTML")
    except MessageTextIsEmpty:
        await bot.send_message(chat_id=message.from_user.id, text="Задолженностей не найдено")


"""
ОТПРАВЛЕНИЕ СООБЩЕНИЯ КУРТОРУ
"""


async def writing_message_to_teacher(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id, text='Наберите сообщение для куратора')
    await ClientStates.message.set()


async def confirmation_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['message'] = message.text
    await bot.send_message(chat_id=message.from_user.id, text='Уверены ли вы, что хотите отправить сообщение?',
                           reply_markup=client_kb.kb_confirmation)
    await ClientStates.confirmation_message.set()


async def send_message_to_teacher(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        teacher_id = await users_db.get_teacher_id(message.from_user.id)
        message_text = data['message']
        name_student = await users_db.get_name_student(message.from_user.id)
        await bot.send_message(chat_id=teacher_id, text=f"<b>Сообщение от студента {name_student}:</b>\n{message_text}",
                               parse_mode="HTML")
    await bot.send_message(chat_id=message.from_user.id, text="Сообщение успешно отправлено",
                           reply_markup=client_kb.kb_client_commands)
    await ClientStates.commands.set()


"""
ИЗМЕНЕНИЕ ИМЕНИ
"""


async def rename_start(message: types.Message):
    name = await users_db.get_name_student(message.from_user.id)
    await bot.send_message(chat_id=message.from_user.id, text=f"Ваше имя <b>{name}</b>", parse_mode="HTML")
    await bot.send_message(chat_id=message.from_user.id, text='Напишите свое новое имя')
    await ClientStates.rename.set()


async def confirmation_rename(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['new_name'] = message.text
    await bot.send_message(chat_id=message.from_user.id, text='Уверены ли вы, что хотите изменить имя?',
                           reply_markup=client_kb.kb_confirmation)
    await ClientStates.confirmation_rename.set()


async def rename_set(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await users_db.rename_student(message.from_user.id, data['new_name'])
    await bot.send_message(chat_id=message.from_user.id, text="Имя успешно изменено",
                           reply_markup=client_kb.kb_client_commands)
    await ClientStates.commands.set()


"""
ПРОЧЕЕ
"""


async def cancel_action(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id, text="Действие отменено",
                           reply_markup=client_kb.kb_client_commands)
    await ClientStates.commands.set()


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(show_all_debts, text="Показать все долги", state=ClientStates.commands)
    dp.register_message_handler(writing_message_to_teacher, text="Отправить сообщение куратору",
                                state=ClientStates.commands)
    dp.register_message_handler(confirmation_message, state=ClientStates.message)
    dp.register_message_handler(send_message_to_teacher, text="Подтвердить", state=ClientStates.confirmation_message)
    dp.register_message_handler(cancel_action, text="Отмена", state=ClientStates)
    dp.register_message_handler(rename_start, text="Изменить имя", state=ClientStates.commands)
    dp.register_message_handler(confirmation_rename, state=ClientStates.rename)
    dp.register_message_handler(rename_set, text="Подтвердить", state=ClientStates.confirmation_rename)
