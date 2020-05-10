import psycopg2
from config import DB_CONFIG
import random


class PgAPI(object):
    def __init__(self, database, user, password=""):
        self.connection = psycopg2.connect(database=database,
                                           user=user,
                                           password=password)

    def init_tables(self):
        """Функция для создания таблиц в базе данных"""
        cur = self.connection.cursor()

        cur.execute('''
            CREATE TABLE Cities
            (id SERIAL PRIMARY KEY,
            name VARCHAR(40) NOT NULL CONSTRAINT Cities_unique_name UNIQUE,
            parser_tag VARCHAR(40) NOT NULL CONSTRAINT Tag_unique_name UNIQUE
            );

            CREATE TABLE Places
            (id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL CONSTRAINT Places_unique_name UNIQUE,
            city_id INT REFERENCES Cities(id) ON DELETE SET NULL,
            address VARCHAR(60) NOT NULL
            );

           CREATE TABLE Categories
            (id SERIAL PRIMARY KEY,
            name VARCHAR(40) NOT NULL CONSTRAINT Categories_unique_name UNIQUE,
            tag VARCHAR(10) NOT NULL CONSTRAINT Categories_unique_tag UNIQUE
            );

            CREATE TABLE Events
            (id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL CONSTRAINT Events_unique_name UNIQUE,
            category INT REFERENCES Categories(id) ON DELETE SET NULL,
            city_id INT REFERENCES Cities(id) ON DELETE SET NULL,
            place_id INT REFERENCES Places(id) ON DELETE SET NULL,
            url TEXT,
            start_datetime TIMESTAMP,
            finish_datetime TIMESTAMP
            );

            CREATE TABLE Users
            (id SERIAL PRIMARY KEY,
            telegram_id INT NOT NULL CONSTRAINT Users_unique_chat_id UNIQUE,
            city_id INT REFERENCES Cities(id) ON DELETE SET NULL,
            categories INT[],
            subscribed BOOL DEFAULT False
            );

            CREATE TABLE Messages
            (id SERIAL PRIMARY KEY,
            user_id INT NOT NULL REFERENCES Users(id) ON DELETE SET NULL,
            type VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        self.connection.commit()

    def send_daily(self):
        """ Возврат событий всем подписанным пользователям
        :return: [{tg_id: _, events: [..]}, ..]
        """
        users = self.get_all_users()
        messages = [{'telegram_id': user['telegram_id'],
                     'events': self.send_user_events(user['telegram_id'])
                     }
                    for user in users]
        return messages

    def add_user(self, telegram_id):
        """Добавление пользователя в базу данных.
        telegram_id: int
        """
        cur = self.connection.cursor()
        try:
            cur.execute('''
                        INSERT INTO Users (telegram_id) VALUES (%s);
                        ''', (telegram_id,))
            self.connection.commit()
            if cur.statusmessage[-1] == '0':
                return False
            return True
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()
            return False

    def delete_user(self, telegram_id):
        """Удаление пользователя из базы данных.
        telegram_id: int
        """
        cur = self.connection.cursor()
        try:
            cur.execute('''
                        DELETE FROM Users
                        WHERE telegram_id=%s;
                        ''', (telegram_id,))
            self.connection.commit()
            if cur.statusmessage[-1] == '0':
                return False
            return True
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()
            return False

    def add_place(self, name, address, city_name=None):
        """Добавление Места в базу данных.
        address: str
        """
        cur = self.connection.cursor()
        city_id = self.find_city(city_name) if city_name else None
        try:
            cur.execute('''
                        INSERT INTO Places (name, city_id, address)
                        VALUES (%s, %s, %s);
                        ''', (name, city_id, address))
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()

    def add_event(self, name, category,
                  finish_datetime, start_datetime=None,
                  city_name=None, place_name=None, url=None):
        """Добавление События в базу данных.
        url: str
        start_datetime, finish_datetime: datetime
        """
        self.add_category(category['name'], category['tag'])

        cur = self.connection.cursor()
        city_id = self.find_city(city_name) if city_name else None
        place_id = self.find_place(place_name) if place_name else None
        category_id = self.find_category(category['name'])

        try:
            cur.execute('''
                        INSERT INTO Events
                        (name, category, city_id, place_id, url,
                        start_datetime, finish_datetime)
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                        ''', (name, category_id, city_id, place_id, url,
                              start_datetime, finish_datetime))
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()

    def add_city(self, name, tag):
        """Добавление города в базу данных.
        name: str
        tag: str
        """
        cur = self.connection.cursor()
        try:
            cur.execute('''
                        INSERT INTO Cities
                        (name, parser_tag)
                        VALUES (%s, %s);
                        ''', (name, tag))
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()

    def add_category(self, name, tag):
        """Добавление категории в базу данных."""
        cur = self.connection.cursor()
        try:
            cur.execute('''
                        INSERT INTO Categories (name, tag) VALUES (%s, %s);
                        ''', (name, tag))
            self.connection.commit()
            if cur.statusmessage[-1] == '0':
                return False
            return True
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()
            return False

    def delete_category(self, name):
        """Удаление категории из базы данных по имени"""
        cur = self.connection.cursor()
        try:
            cur.execute('''
                        DELETE FROM Categories
                        WHERE name = %s;
                        ''', (name, ))
            self.connection.commit()
            if cur.statusmessage[-1] == '0':
                return False
            return True
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()
            return False

    def find_city(self, city_name):
        """Поиск id города по названию"""
        cur = self.connection.cursor()
        cur.execute('''
                    SELECT id FROM Cities WHERE name = %s
                    ''', (city_name,))
        city_id = cur.fetchone()
        return city_id[0] if city_id else None

    def find_place(self, place_name):
        """Поиск id места по названию"""
        cur = self.connection.cursor()
        cur.execute('''SELECT id FROM Places WHERE name = %s
                    ''', (place_name,))
        place_id = cur.fetchone()
        return place_id[0] if place_id else None

    def find_category(self, category):
        """Нахождение имени id категории по имени"""
        cur = self.connection.cursor()
        cur.execute('''SELECT id FROM Categories WHERE name = %s
                    ''', (category,))
        category_id = cur.fetchone()
        return category_id[0] if category_id else None

    def find_category_by_tag(self, tag):
        """Нахождение id категории по тэгу"""
        cur = self.connection.cursor()
        cur.execute('''SELECT id FROM Categories WHERE tag = %s
                    ''', (tag,))
        category_id = cur.fetchone()
        return category_id[0] if category_id else None

    def delete_old_events(self):
        """удаление неактуальных(прошедших) событий из бд"""
        cur = self.connection.cursor()
        cur.execute('''
                    DELETE FROM Events
                    WHERE finish_datetime < CURRENT_TIMESTAMP;
                    ''')
        self.connection.commit()

    def get_category_name(self, category_id):
        """Получить массив человекоподобных названий категорий"""
        cur = self.connection.cursor()
        cur.execute('''
                    SELECT name From Categories
                    WHERE id = %s;
                    ''', (category_id,))
        resp = cur.fetchone()
        return resp[0] if resp else None

    def get_all_subscribed_users(self):
        """Возвращает список всех подписанных пользователей"""
        cur = self.connection.cursor()
        cur.execute('''
                    SELECT id, telegrav_id From Users
                    WHERE subscribed=True;
                    ''')
        return cur.fetchall()

    def get_user_categories(self, user_id):
        """Получить массив индексов категорий пользователя"""
        cur = self.connection.cursor()
        cur.execute('''
                    SELECT categories From Users
                    WHERE telegram_id=%s
                    ''', (user_id,))
        categories = cur.fetchone()
        return [categories[0]][0] if categories[0] else []

    def set_user_category(self, user_id, category_tag):
        """Добавляет новую категорию пользователю"""
        old_categories = self.get_user_categories(user_id)
        new_category = self.find_category_by_tag(category_tag)
        if new_category and new_category not in old_categories:
            old_categories.append(new_category)
            cur = self.connection.cursor()
            cur.execute('''
                        UPDATE Users
                        SET categories=%s WHERE telegram_id=%s
                        ''', (old_categories, user_id))
            self.connection.commit()
            return True
        else:
            return False

    def clear_user_categories(self, user_id):
        """Удаляет все выбранные категории пользователя"""
        cur = self.connection.cursor()
        cur.execute('''
                    UPDATE Users
                    SET categories=%s WHERE telegram_id=%s
                    ''', ([], user_id))
        self.connection.commit()
        if cur.statusmessage[-1] == '0':
            return False
        else:
            return True

    def set_user_city(self, user_id, city_name):
        """Задаёт город пользователя"""
        city_id = self.find_city(city_name)
        cur = self.connection.cursor()
        cur.execute('''
                     UPDATE Users
                     SET city_id=%s WHERE telegram_id=%s
                     ''', (city_id, user_id))
        self.connection.commit()

    def send_user_events(self, user_id, count=1):
        """Функция, которая возвращает пользователю события
        Возвращает n случайных событий из категорий
        которые выбраны у пользователя.
        Если у пользователя не стоят категории, вернуть False
        Если не найдены события, вернуть []
        """
        cur = self.connection.cursor()
        cur.execute('''
                    SELECT categories From Users
                    WHERE telegram_id=%s
                    ''', (user_id,))
        categories = cur.fetchone()[0]
        if not categories:
            return False
        events = []
        for category in categories:
            print(category)
            cur.execute('''
                        SELECT id, name From Events
                        WHERE category = %s
                        ''', (category,))
            category_events = cur.fetchall()
            for event in category_events:
                events.append(event)

        choised_events = []
        for i in range(count):
            item = random.choice(events)
            events.remove(item)
            choised_events.append(item)

        return choised_events

    def set_user_subscribed(self, user_id):
        """Подписать пользователя на рассылку"""
        cur = self.connection.cursor()
        cur.execute('''
                     UPDATE Users
                     SET subscribed=True
                     WHERE telegram_id=%s AND subscribed=False
                     ''', (user_id,))
        if cur.statusmessage[-1] == '0':
            return False
        else:
            self.connection.commit()
            return True

    def clear_user_subscribed(self, user_id):
        """Отписать пользователя от рассылки"""
        cur = self.connection.cursor()
        cur.execute('''
                     UPDATE Users
                     SET subscribed=False
                     WHERE telegram_id=%s AND subscribed=True
                     ''', (user_id,))
        if cur.statusmessage[-1] == '0':
            return False
        else:
            self.connection.commit()
            return True

    def get_event(self, id):
        """Возвращает одно событие из базы"""
        cur = self.connection.cursor()
        cur.execute('''
                     SELECT * From Events
                     WHERE id=%s
                     ''', (id,))
        return cur.fetchall()


def init_db(database_config):
    """Функция для вызова инициализации таблиц в бд"""
    db = PgAPI(**database_config)
    db.init_tables()


if __name__ == '__main__':
    init_db(DB_CONFIG)
