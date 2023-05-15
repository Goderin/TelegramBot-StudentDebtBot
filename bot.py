from aiogram.utils import executor

from create_bot import dp
from handlers import registration, admin, client, other
from databases import users_db, debts_db


async def on_startup(_):
    await users_db.db_users_start()
    await debts_db.db_debts_start()
    print("Машина запущена")


registration.register_handlers_start_command(dp)
registration.register_handlers_registration_teacher(dp)
registration.register_handlers_registration_student(dp)

admin.register_handlers_admin(dp)

client.register_handlers_client(dp)

other.register_handlers_other(dp)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
