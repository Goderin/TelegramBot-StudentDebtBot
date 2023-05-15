from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import TOKEN_API

bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage=MemoryStorage())
