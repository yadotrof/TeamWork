import logging
from aiogram import Bot, Dispatcher, executor, types
from config import TG_TOKEN
from bot_api import TelegramAPI

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler()
async def command_cmd_handler(message: types.Message):
    response, keyboard_markup = TelegramAPI.process_message(message)
    await message.reply(response, reply_markup=keyboard_markup)


@dp.callback_query_handler(text='cinema')
@dp.callback_query_handler(text='stand-up')
@dp.callback_query_handler(text='festival')
@dp.callback_query_handler(text='concert')
async def inline_answer_callback_handler(query: types.CallbackQuery):
    response = TelegramAPI.categories_command(query)
    await bot.send_message(query.from_user.id, response)


@dp.callback_query_handler(text='msk')
@dp.callback_query_handler(text='spb')
async def inline_answer_callback_handler(query: types.CallbackQuery):
    response = TelegramAPI.categories_command(query)
    await bot.send_message(query.from_user.id, response)


@dp.callback_query_handler()
async def inline_answer_callback_handler(query: types.CallbackQuery):
    response = TelegramAPI.process_callback(query)
    await bot.send_message(query.from_user.id, response)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
