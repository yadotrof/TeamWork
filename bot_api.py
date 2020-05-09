from abc import ABC, abstractmethod
from pg_api import PgAPI
from aiogram import types


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
            'help': 'help_command',
            'start': 'start_command',
            'registration': 'registration_command',
            'categories': 'categories_command',
            'find': 'find_command'
        }
        func = bot_commands.get(message.get_command(),
                                lambda: "Я пока не знаю такой команды")
        return func(self, message)

    def start_command(self, data):
        text = 'привет, я бот, который подскажет, куда тебе сходить ' \
               'в свободное время, для начала расскажи о себе ' \
               '/registration ^^ '
        self.db.add_user(data.from_user)

    @staticmethod
    def registration_command(data):
        text = 'Выбери город'
        keyboard_markup = types.InlineKeyboardMarkup(row_width=2)
        text_and_data = (
            ('Moscow', 'msk'),
            ('Saint Petersburg', 'spb'),
        )
        row_btn = (types.InlineKeyboardButton(text, callback_data=data)
                   for text, data in text_and_data)
        keyboard_markup.row(*row_btn)

        return text, keyboard_markup

    def set_subscriber(self, data):
        # TODO нужна функци добавления инфы о подписке в бд
        return 0

    def process_callback(self, query):
        answer_data = query.data
        bot_callback = {
            'find': 'find_command',
            'clean': 'clean_command'
        }
        func = bot_callback.get(answer_data,
                                lambda: "Я пока не знаю такой команды")
        return func(self, answer_data)

    def process_city(self, data):
        self.set_city(data)
        text = "давай посмотрим, что ты больше любишь /categories"
        return text

    @staticmethod
    def categories_command(self, data):
        # TODO нужна функция на вытащить доступные категории из базы
        # запрос на те которые выбраны у пользователя
        # разница между ними- то из чего предлагаем выбирать
        user_tags = self.db.get_user_categories(data.from_user.id)
        text = f'Сейчас у тебя выбраны:__ЗАПРОС_К_БД'
        # 'отметь другие категории или нажми /find и мы найдем' \
        # 'что нибудь по этим'

        keyboard_markup = types.InlineKeyboardMarkup(row_width=6)
        categories = (('Кино', 'cinema'),
                      ('Стенд-ап', 'stand-up'),
                      ('Концерт', 'concert'),
                      ('Фестиваль', 'festival'),
                      ('Завершить выбор и начать поиск', 'find'),
                      ('Сбросить все выбранные', 'clean'))

        row_btn = (types.InlineKeyboardButton(text, callback_data=data)
                   for text, data in categories)
        keyboard_markup.row(*row_btn)
        return text, keyboard_markup

    def process_categories(self, data):
        # TODO нужен метод на вытащить ссылки событий из базы
        # добавляем выбранную категорию у списку пользвателя
        self.db.set_user_category(data)
        self.categories_command(data)

    @staticmethod
    def help_command(self):
        text = 'Для начала работы /start\nДля выбора города' \
               ' /registration\nДля настройки категорий ' \
               '/categories\n'
        return text

    def find_command(self, data):
        text = "Смотри, куда можно сходить\n"
        events = self.get_event(data)
        return text + "\n".join(events)

    def clean_command(self, data):
        # почистить выбранные категории пользователя в бд
        self.categories_command(data)
