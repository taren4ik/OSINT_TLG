import os
import logging
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from aiogram import Bot, Dispatcher, executor, types

load_dotenv()

token = os.getenv('TOKEN')
# api_id = os.getenv('API_ID')
# api_hash = os.getenv('API_HASH')


bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
# Диспетчер для бота
dp = Dispatcher(bot)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    await message.answer('Привет, {}. Введите название чата '.format(
        message.from_user.first_name))


@dp.message_handler(types="text")
async def cmd_choice(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_1 = types.KeyboardButton(text="Пользователи")
    keyboard.add(button_1)
    button_2 = "Сообщения"
    keyboard.add(button_2)
    await message.answer("Что будем парсить?", reply_markup=keyboard)


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
