import psycopg2


class PgAPI(object):
    def __init__(self, database, user, password=""):
        self.connection = psycopg2.connect(database=database,
                                           user=user,
                                           password=password)

    def set_city(self, data):
        """data = {chat_id: int, city: str}"""
        pass

    def set_preferences(self, data):
        """data = {chat_id: int, category: str}"""
        pass

    def get_event(self, data):
        """data = {chat_id: int}"""
        pass

    def init_tables(self):
        """Функция для создания таблиц в базе данных"""
        cur = self.connection.cursor()

        cur.execute('''
            CREATE TABLE Cities
            (id SERIAL PRIMARY KEY,
            name VARCHAR(40) NOT NULL CONSTRAINT Cities_unique_name UNIQUE
            );

            CREATE TABLE Places
            (id SERIAL PRIMARY KEY,
            name VARCHAR(40) NOT NULL CONSTRAINT Places_unique_name UNIQUE,
            city_id INT REFERENCES Cities(id),
            address VARCHAR(60) NOT NULL
            );

            CREATE TABLE Events
            (id SERIAL PRIMARY KEY,
            name VARCHAR(40) NOT NULL CONSTRAINT Events_unique_name UNIQUE,
            city_id INT REFERENCES Cities(id),
            place_id INT REFERENCES Places(id),
            url TEXT,
            datetime TIMESTAMP
            );
            
            CREATE TABLE Users
            (id SERIAL PRIMARY KEY,
            telegram_id INT NOT NULL CONSTRAINT Users_unique_chat_id UNIQUE,
            city_id INT REFERENCES Cities(id)
            );

            CREATE TABLE Messages
            (id SERIAL PRIMARY KEY,
            user_id INT NOT NULL REFERENCES Users(id),
            type VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        self.connection.commit()
