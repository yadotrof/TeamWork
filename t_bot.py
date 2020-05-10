import logging
from aiogram import Bot, Dispatcher, executor, types
from config import TG_TOKEN, DB_CONFIG
from bot_api import TelegramAPI, BotAPI

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)
database_config = DB_CONFIG
bot_api = TelegramAPI(database_config)



@dp.message_handler(commands='categories')
async def command_cmd_handler(message: types.Message):
    response, keyboard_markup = TelegramAPI.categories_command(
        self=bot_api, query=message)
    await message.reply(response, reply_markup=keyboard_markup)


@dp.message_handler(commands='start')
async def command_cmd_handler(message: types.Message):
    response = TelegramAPI.start_command(self=bot_api,
                                         message=message)
    await message.reply(response)


@dp.message_handler(commands='registration')
async def command_cmd_handler(message: types.Message):
    response, keyboard_markup = TelegramAPI.registration_command(
        data=message)
    await message.reply(response, reply_markup=keyboard_markup)


@dp.message_handler(commands='find')
async def command_cmd_handler(message: types.Message):
    response = TelegramAPI.find_command(self=bot_api, data=message)
    await message.reply(response)


@dp.message_handler(commands='help')
async def command_cmd_handler(message: types.Message):
    response = TelegramAPI.help_command()
    await message.reply(response)


@dp.callback_query_handler(text=['cinema', 'stand-up',
                                 'festival', 'concert', 'stand-up'])
async def inline_answer_callback_handler(query: types.CallbackQuery):
    TelegramAPI.process_categories(self=bot_api, query=query)
    response, keyboard_markup = TelegramAPI.categories_command(
        self=bot_api, query=query)
    await bot.send_message(query.from_user.id, response,
                           reply_markup=keyboard_markup)


@dp.callback_query_handler(text='msk')
@dp.callback_query_handler(text='spb')
async def inline_answer_callback_handler(query: types.CallbackQuery):
    response = TelegramAPI.process_city(self=bot_api, query= query)
    await bot.send_message(query.from_user.id, response)


@dp.callback_query_handler(text='find')
@dp.callback_query_handler(text='clean')
async def inline_answer_callback_handler(query: types.CallbackQuery):
    response = TelegramAPI.process_callback(query=query)
    await bot.send_message(query.from_user.id, response)


@dp.message_handler(commands='subscribe')
async def command_cmd_handler(message: types.Message):
    response = TelegramAPI.subscribe_command(self=bot_api,
                                             data=message)
    await message.reply(response)


@dp.message_handler(commands='unsubscribe')
async def command_cmd_handler(message: types.Message):
    response = TelegramAPI.unsubscribe_command(self=bot_api,
                                               data=message)
    await message.reply(response)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
