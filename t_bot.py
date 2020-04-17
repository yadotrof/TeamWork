import logging
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = '802367623:AAGeVxDzQoqhczo4jENgtOSYJ5b5GHva_MY'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands='start')
async def start_cmd_handler(message: types.Message):
    text = 'привет, я бот, который подскажет, куда тебе сходить в свободное время, для начала расскажи о себе ' \
           '/registration ^^ '
    await message.reply(text)
    

@dp.message_handler(commands='registration')
async def registration_cmd_handler(message: types.Message):
    text = 'для начала выбери город'
    keyboard_markup = types.InlineKeyboardMarkup(row_width=2)

    text_and_data = (
        ('Moscow', 'msk'),
        ('Saint Petersburg', 'spb'),
    )

    row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
    keyboard_markup.row(*row_btns)
    await message.reply(text,  reply_markup=keyboard_markup)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

