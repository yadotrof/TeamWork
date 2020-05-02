from abc import ABC, abstractmethod
from pg_api import PgAPI
from aiogram import Bot, Dispatcher, executor, types


class BotAPI(ABC):
    """Базовый класс для API разных ботов.
    Дочерние классы обрабатывают особенности оболочек
    и передают базе данных необходимые запросы.
    """
    @abstractmethod
    def set_city(self, data):
        pass

    @abstractmethod
    def set_preferences(self, data):
        pass

    @abstractmethod
    def get_event(self, data):
        pass

    @abstractmethod
    def process_message(self, data):
        pass

    @abstractmethod
    def set_subsciber(self, data):
        pass


class TelegramAPI(BotAPI):
    def __init__(self, config):
        self.db = PgAPI(**config)

    def set_db(self, config):
        """config = {database: str, user: str[, password: str]}"""
        self.db = PgAPI(**config)

    @staticmethod
    def convert_data(data):
        """Метод для преобразования сообщения из Telegram
        в данные, сериализованые для бота.
        """
        return data

    def set_city(self, data):
        converted_data = self.convert_data(data)
        self.db.set_city(converted_data)

    def set_preferences(self, data):
        converted_data = self.convert_data(data)
        self.db.set_preferences(converted_data)

    def get_event(self, data):
        converted_data = self.convert_data(data)
        self.db.get_event(converted_data)

    def process_message(self, message):
        # TODO что там с обработкой данных convert_data ??
        bot_commands = {
            'start': 'start_command',
            'registration': 'registration_command'
        }
        func = bot_commands.get(message.get_command(), lambda: "Я пока не знаю такой команды")
        func(message)

    def start_command(self, data):
        text = 'привет, я бот, который подскажет, куда тебе сходить ' \
               'в свободное время, для начала расскажи о себе ' \
               '/registration ^^ '

        self.set_subscriber(data.from_user)

    @staticmethod
    def registration_command(data):
        text = 'Выбери город'
        keyboard_markup = types.InlineKeyboardMarkup(row_width=2)
        text_and_data = (
            ('Moscow', 'msk'),
            ('Saint Petersburg', 'spb'),
        )
        row_btns = (types.InlineKeyboardButton(text, callback_data=data)
                    for text, data in text_and_data)
        keyboard_markup.row(*row_btns)

        return text, keyboard_markup

    def set_subscriber(self, data):
        # TODO нужна функци добавления инфы о подписке в бд
        return 0
