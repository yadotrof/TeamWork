import logging
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = '802367623:AAGeVxDzQoqhczo4jENgtOSYJ5b5GHva_MY'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands='start')
async def start_cmd_handler(message: types.Message):
    text = 'привет, я бот, который подскажет, куда тебе сходить ' \
           'в свободное время, для начала расскажи о себе ' \
           '/registration ^^ '
    await message.reply(text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

