import unittest
from pg_api import PgAPI
from config import TEST_DB_CONFIG


class TestStringMethods(unittest.TestCase):
    """Тестирование работы с базой данных"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = PgAPI(**TEST_DB_CONFIG)
        self.db.clear_data()

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
        self.assertFalse(self.db.add_category(category['name'],
                                              category['tag']))
        self.assertTrue(self.db.delete_category(category['name']))
        self.assertFalse(self.db.delete_category(category['name']))

    def test_user_categories(self):
        """Тестирование категорий предпочтений пользователя"""
        user_tg_id = 3
        category = {'name': "Кино", 'tag': 'cinema'}
        self.assertTrue(self.db.add_user(user_tg_id))
        self.assertEqual(self.db.get_user_categories(user_tg_id), [])
        self.assertTrue(self.db.add_category(category['name'],
                                             category['tag']))
        self.assertTrue(self.db.set_user_category(user_tg_id,
                                                  category['name']))
        self.assertEqual(self.db.get_category_name(
            self.db.get_user_categories(user_tg_id)[0]), 'Кино')
        self.assertFalse(self.db.set_user_category(user_tg_id,
                                                   category['name']))
        self.assertTrue(self.db.delete_category(category['name']))
        self.assertTrue(self.db.delete_user(user_tg_id))


if __name__ == '__main__':
    unittest.main()
