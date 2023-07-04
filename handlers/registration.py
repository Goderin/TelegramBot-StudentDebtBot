from create_bot import bot
from keyboards import registration_kb, admin_kb, client_kb
from handlers.client import ClientStates

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from databases import users_db


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
        await bot.send_message(chat_id=message.from_user.id,
                               text="Добро пожаловать на страницу бота для упрощенной работы кураторов и студентов с задолженностями!\n Введите свой идентификатор")
        await RegistrationTeacherStates.code.set()
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Вы уже зарегестрированы!")


async def check_id(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['identifier'] = message.text
    if await users_db.check_identifier(data['identifier']):
        role = await users_db.add_user(data['identifier'], message.from_user.id)
        if role == 1:
            await bot.send_message(chat_id=message.from_user.id, text="Вы успешно зарегистрировались, как студент",
                                   reply_markup=client_kb.kb_client_commands)
            await ClientStates.commands.set()
        if role == 2:
            await bot.send_message(chat_id=message.from_user.id, text="Вы успешно зарегистрировались, как куратор",
                                   reply_markup=admin_kb.kb_select_student)
            await state.finish()

        if role == 3:
            await bot.send_message(chat_id=message.from_user.id, text="Вы успешно зарегистрировались, как сотрудик")
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Вашего идентификатора нет в базе данных.\n Попробуйте снова, либо обратитесь к сотруднику")


def register_handlers_start_command(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'], state="*")
    dp.register_message_handler(check_id, state=RegistrationTeacherStates.code)