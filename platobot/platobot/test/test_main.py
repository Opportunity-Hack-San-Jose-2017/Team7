import unittest
from platobot.factories.app import create_app
from platobot import config
from platobot.config import TestConfig

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

    def tearDown(self):
        """teardown all initialized variables."""
        pass

    def assertStatus(self, res, status_code):
        self.assertEqual(res.status_code, status_code)

    def assertResponseText(self, res, text):
        self.assertTrue(text in res.data)
