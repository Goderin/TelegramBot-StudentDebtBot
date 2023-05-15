from create_bot import bot
from keyboards import registration_kb, admin_kb, client_kb
from handlers.client import ClientStates

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from databases import users_db, debts_db
from config import PASSWORD_TEACHER


class RegistrationStudentStates(StatesGroup):
    full_name = State()
    group = State()


class RegistrationTeacherStates(StatesGroup):
    code = State()
    full_name = State()
    group = State()


async def start_command(message: types.Message) -> None:
    await message.delete()
    if not await users_db.check_registration(message.from_user.id):
        await bot.send_message(chat_id=message.from_user.id, text="Добро пожаловать на страницу бота для упрощенной работы кураторов и студентов с задолженностями!\n Выберите тип пользователя, который хотите создать.",
                               reply_markup=registration_kb.select_role())
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Вы уже зарегестрированы!")


# РЕГИСТРАЦИЯ ПРЕПОДАВАТЕЛЯ-------------------------------------------------------------------------------------------
async def registration_teacher(callback: types.CallbackQuery) -> None:
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id,
                           text="Для проверки подленности выбранного типа пользователя введите выданный вам код:")
    await RegistrationTeacherStates.code.set()


async def check_registration_code(message: types.Message, state: FSMContext) -> None:
    if message.text == PASSWORD_TEACHER:
        await bot.send_message(chat_id=message.from_user.id,
                               text='Отлично, давайте продолжим регистрацию. Теперь введите свое имя и фамилию')
        await RegistrationTeacherStates.next()
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text='К сожалению вы не прошли проверку, попробуйте снова. Для этого введите комманду /start')
        await state.finish()


async def load_full_name_teacher(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['user_id'] = message.from_user.id
        data['full_name'] = message.text
    await bot.send_message(chat_id=message.from_user.id, text="Теперь напишите свою группу(Пример: <b>ИСТ-21-2Б</b>)",
                           parse_mode="HTML")
    await RegistrationTeacherStates.next()


async def load_group_teacher(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['group'] = message.text
    if await debts_db.is_table_exists(data['group']):
        await users_db.add_teacher(data['user_id'], data['full_name'], data['group'])
        await bot.send_message(chat_id=message.from_user.id, text='Отлично, ваш аккаунт создан!', reply_markup=admin_kb.kb_select_student)
        await state.finish()
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Такой группы не существует, введите заново")


# -----------------------------------------------------------------------------------------------------------------------

# РЕГИСТРАЦИЯ СТУДЕНТА-------------------------------------------------------------------------------------------
async def registration_student(callback: types.CallbackQuery) -> None:
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id,
                           text="Привет студент, давай зарегестрируемся! Для начала введи свое имя и фамилию")
    await RegistrationStudentStates.full_name.set()


async def load_full_name_student(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['user_id'] = message.from_user.id
        data['full_name'] = message.text
    await bot.send_message(chat_id=message.from_user.id, text="Теперь напиши свою группу(Пример: <b>ИСТ-21-2Б</b>)",
                           parse_mode="HTML")
    await RegistrationStudentStates.next()


async def load_group_student(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['group'] = message.text
    if await debts_db.is_table_exists(data['group']):
        await users_db.add_student(data['user_id'], data['full_name'], data['group'])
        await debts_db.add_user_id_students(data['group'], data['user_id'])
        await bot.send_message(chat_id=message.from_user.id, text="Отлично, ты зарегестрирован!",
                               reply_markup=client_kb.kb_client_commands)
        await ClientStates.commands.set()
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Такой группы не существует, введите заново")


def register_handlers_start_command(dp: Dispatcher) -> None:
    dp.register_message_handler(start_command, commands=['start'], state="*")


def register_handlers_registration_teacher(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(registration_teacher, lambda callback_query: callback_query.data == 'teacher')
    dp.register_message_handler(check_registration_code, state=RegistrationTeacherStates.code)
    dp.register_message_handler(load_full_name_teacher, state=RegistrationTeacherStates.full_name)
    dp.register_message_handler(load_group_teacher, state=RegistrationTeacherStates.group)


def register_handlers_registration_student(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(registration_student, lambda callback_query: callback_query.data == 'student')
    dp.register_message_handler(load_full_name_student, state=RegistrationStudentStates.full_name)
    dp.register_message_handler(load_group_student, state=RegistrationStudentStates.group)
