import unittest
from pg_api import PgAPI
from config import TEST_DB_CONFIG
import os


class TestStringMethods(unittest.TestCase):
    """Тестирование работы с базой данных"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = PgAPI(**TEST_DB_CONFIG)

    def test_user_creation(self):
        """Тестирование добавление и удаления пользователя"""
        user_tg_id = 0
        self.assertTrue(self.db.add_user(user_tg_id))
        self.assertFalse(self.db.add_user(user_tg_id))
        self.assertTrue(self.db.delete_user(user_tg_id))
        self.assertFalse(self.db.delete_user(user_tg_id))

    def test_user_flags(self):
        """Тестирование выставления флагов подписок и отписок"""
        user_tg_id = 1
        self.assertTrue(self.db.add_user(user_tg_id))
        self.assertFalse(self.db.clear_user_subscribed(user_tg_id))
        self.assertTrue(self.db.set_user_subscribed(user_tg_id))
        self.assertFalse(self.db.set_user_subscribed(user_tg_id))
        self.assertTrue(self.db.clear_user_subscribed(user_tg_id))
        self.assertFalse(self.db.clear_user_subscribed(user_tg_id))
        self.assertTrue(self.db.delete_user(user_tg_id))

    def test_categories_creation(self):
        """Тестирование созданий категорий"""
        user_tg_id = 2
        category = {'name': "Кино", 'tag': 'cinema'}
        self.assertIsNone(self.db.get_category_name(1))
        self.assertFalse(self.db.delete_category(category['name']))
        self.assertTrue(self.db.add_category(category['name'],
                                             category['tag']))
        self.assertEqual(self.db.get_category_name(1), 'Кино')
        self.assertFalse(self.db.add_category(category['name'],
                                              category['tag']))
        self.assertTrue(self.db.delete_category(category['name']))
        self.assertFalse(self.db.delete_category(category['name']))

    def test_simple(self):
        """Тестирование категорий предпочтений пользователя"""
        user_tg_id = 3
        category = {'name': "Кино", 'tag': 'cinema'}
        another_category = {'name': "Кино2", 'tag': 'cinema2'}
        self.assertTrue(self.db.add_user(user_tg_id))

        self.assertTrue(self.db.add_category(category['name'],
                                             category['tag']))
        self.assertTrue(self.db.add_category(another_category['name'],
                                             another_category['tag']))
        self.assertTrue(self.db.set_user_category(user_tg_id,
                                                  category['tag']))
        self.assertTrue(self.db.set_user_category(user_tg_id,
                                                  another_category['tag']))
        self.assertEqual(self.db.get_user_categories(user_tg_id),
                         [self.db.find_category('Кино'),
                          self.db.find_category('Кино2')])
        self.assertTrue(self.db.clear_user_categories(user_tg_id))
        self.assertEqual(self.db.get_user_categories(user_tg_id), [])


if __name__ == '__main__':
    os.system('psql -U postgres -d postgres -c '
              '"DROP DATABASE IF EXISTS {};"'.format(
                    TEST_DB_CONFIG['database']))
    os.system('psql -U postgres -d postgres -c '
              '"CREATE DATABASE {};"'.format(
                    TEST_DB_CONFIG['database']))
    PgAPI(**TEST_DB_CONFIG).init_tables()
    unittest.main()
