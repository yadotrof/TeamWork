from abc import ABC, abstractmethod
from pg_api import PgAPI


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
