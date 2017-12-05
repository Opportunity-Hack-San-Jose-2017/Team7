import unittest
from platobot.factories.app import create_app, reinit_db
from platobot import config, models
from platobot.utils import database
from platobot.config import TestConfig

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        """Define test variables and initialize app."""
        print('set up')
        self.app = create_app(TestConfig())
        self.db = reinit_db(TestConfig())
        self.client = self.app.test_client()

    def tearDown(self):
        """teardown all initialized variables."""
        pass

    def assertStatus(self, res, status_code):
        self.assertEqual(res.status_code, status_code)

    def assertResponseText(self, res, text):
        self.assertTrue(text in res.data)
