import psycopg2
from config import DB_CONFIG


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
            city_id INT REFERENCES Cities(id),
            address VARCHAR(60) NOT NULL
            );

            CREATE TABLE Events
            (id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL CONSTRAINT Events_unique_name UNIQUE,
            categories INT[],
            city_id INT REFERENCES Cities(id),
            place_id INT REFERENCES Places(id),
            url TEXT,
            start_datetime TIMESTAMP,
            finish_datetime TIMESTAMP 
            );

            CREATE TABLE Users
            (id SERIAL PRIMARY KEY,
            telegram_id INT NOT NULL CONSTRAINT Users_unique_chat_id UNIQUE,
            city_id INT REFERENCES Cities(id),
            categories INT[],
            subscribed BOOL DEFAULT False
            );

            CREATE TABLE Messages
            (id SERIAL PRIMARY KEY,
            user_id INT NOT NULL REFERENCES Users(id),
            type VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE Categories
            (id SERIAL PRIMARY KEY,
            name VARCHAR(40) NOT NULL CONSTRAINT Categories_unique_name UNIQUE,
            tag VARCHAR(10) NOT NULL CONSTRAINT Categories_unique_tag UNIQUE
            )
        ''')
        self.connection.commit()

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
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()

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

    def add_event(self, name, categories,
                  finish_datetime, start_datetime=None,
                  city_name=None, place_name=None, url=None):
        """Добавление События в базу данных.
        url: str
        datetime: datetime
        """
        for category in categories:
            self.add_category(category['name'], category['tag'])
        cur = self.connection.cursor()
        city_id = self.find_city(city_name) if city_name else None
        place_id = self.find_place(place_name) if place_name else None

        categories_ids = [self.find_category(category['name'])
                          for category in categories]
        try:
            cur.execute('''
                        INSERT INTO Events
                        (name, categories, city_id, place_id, url, 
                        start_datetime, finish_datetime)
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                        ''', (name, categories_ids, city_id, place_id, url,
                              start_datetime, finish_datetime))
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()

    def add_city(self, name, tag):
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
        cur = self.connection.cursor()
        try:
            cur.execute('''
                        INSERT INTO Categories (name, tag) VALUES (%s, %s);
                        ''', (name, tag))
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()

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

    def delete_old_events(self):
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
        return cur.fetchall()

    def get_user_categories(self, user_id):
        """Получить массив индексов категорий пользователя"""
        cur = self.connection.cursor()
        cur.execute('''
                    SELECT categories From Users
                    WHERE telegram_id=%s
                    ''', (user_id,))
        categories = cur.fetchone()
        return [categories[0]] if categories[0] else []

    def set_user_category(self, user_id, category):
        """Задать новую категорию пользователю"""
        old_categories = self.get_user_categories(user_id)
        new_category = self.find_category(category)
        if new_category not in old_categories:
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

    def set_user_city(self, user_id, city_name):
        """data = {chat_id: int, city: str}"""

        city_id = self.find_city(city_name)
        cur = self.connection.cursor()
        cur.execute('''
                     UPDATE Users
                     SET city_id=%s WHERE telegram_id=%s
                     ''', (city_id, user_id))
        self.connection.commit()

    def send_user_event(self, data):
        """data = {chat_id: int}"""
        pass

    def set_user_subscribed(self, user_id):
        """Подписать пользователя на рассылку"""
        cur = self.connection.cursor()
        cur.execute('''
                     UPDATE Users
                     SET subscribed=True 
                     WHERE telegram_id=%s AND subscribed=False
                     ''', (user_id, ))
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
                     ''', (user_id, ))
        if cur.statusmessage[-1] == '0':
            return False
        else:
            self.connection.commit()
            return True


def init_db(database_config):
    db = PgAPI(**database_config)
    db.init_tables()


if __name__ == '__main__':
    init_db(DB_CONFIG)
