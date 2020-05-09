import logging
from aiogram import Bot, Dispatcher, executor, types
from config import TG_TOKEN
from bot_api import TelegramAPI

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands='categories')
async def command_cmd_handler(message: types.Message):
    response, keyboard_markup = TelegramAPI.categories_command(message)
    await message.reply(response, reply_markup=keyboard_markup)


@dp.message_handler(commands='start')
async def command_cmd_handler(message: types.Message):
    response = TelegramAPI.start_command(message)
    await message.reply(response)


@dp.message_handler(commands='registration')
async def command_cmd_handler(message: types.Message):
    response, keyboard_markup = TelegramAPI.registration_command(message)
    await message.reply(response, reply_markup=keyboard_markup)


@dp.message_handler(commands='find')
async def command_cmd_handler(message: types.Message):
    response = TelegramAPI.find_command(message)
    await message.reply(response)


@dp.message_handler(commands='help')
async def command_cmd_handler(message: types.Message):
    response = TelegramAPI.help_command(message)
    await message.reply(response)


@dp.callback_query_handler(text=['cinema', 'stand-up', 'festival', 'concert', 'stand-up'])
async def inline_answer_callback_handler(query: types.CallbackQuery):
    TelegramAPI.process_categories(query)
    response, keyboard_markup = TelegramAPI.categories_command(query)
    await bot.send_message(query.from_user.id, response, reply_markup=keyboard_markup)


@dp.callback_query_handler(text='msk')
@dp.callback_query_handler(text='spb')
async def inline_answer_callback_handler(query: types.CallbackQuery):
    response = TelegramAPI.process_city(query)
    await bot.send_message(query.from_user.id, response)


@dp.callback_query_handler(text='find')
@dp.callback_query_handler(text='clean')
async def inline_answer_callback_handler(query: types.CallbackQuery):
    response = TelegramAPI.process_callback(query)
    await bot.send_message(query.from_user.id, response)


@dp.message_handler(commands='subscribe')
async def command_cmd_handler(message: types.Message):
    response = TelegramAPI.subscribe_command(message)
    await message.reply(response)


@dp.message_handler(commands='unsubscribe')
async def command_cmd_handler(message: types.Message):
    response = TelegramAPI.unsubscribe_command(message)
    await message.reply(response)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
