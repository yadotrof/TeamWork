import logging
from aiogram import Bot, Dispatcher, executor, types
from config import TG_TOKEN
from bot_api import TelegramAPI

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)


# @dp.message_handler(commands=['start','registration'])
async def command_cmd_handler(message: types.Message):
    response, keyboard_markup = TelegramAPI.process_message(message)
    await message.reply(response, reply_markup=keyboard_markup)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
