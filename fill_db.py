from kuda_go_parser import start_parsing
from pg_api import PgAPI
from config import DB_CONFIG


def fill_db(database_config):
    db = PgAPI(**database_config)
    start_parsing(db)
    #db.delete_old_events()


if __name__ == '__main__':
    fill_db(DB_CONFIG)
