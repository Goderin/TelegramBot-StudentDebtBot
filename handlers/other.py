from aiogram import types, Dispatcher


async def delete_message(message: types.Message) -> None:
    await message.delete()


def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(delete_message, state="*")
