import unittest
import os
import json
from platobot.factories.app import create_app
from platobot import config
from platobot.config import TestConfig

def generate_facebook_quick_reply_message():
    return {
        "object": "page",
        "entry": [
            {
                "id": "490985961270614",
                "time": 1509497381914,
                "messaging": [
                    {
                        "sender": {
                            "id": "1603594916368437"
                        },
                        "recipient": {
                            "id": "490985961270614"
                        },
                        "timestamp": 1509497381562,
                        "message": {
                            "quick_reply": {
                                "payload": "reply2"
                            },
                            "mid": "mid.$cAAG-jMY5wb5lplNqulfdQ4bcTu9Z",
                            "seq": 228148,
                            "text": "No"
                        }
                    }
                ]
            }
        ]
    }

def generate_facebook_message():
    return {
        "object": "page",
        "entry": [
            {
                "id": "490985961270614",
                "time": 1509497461744,
                "messaging": [
                    {
                        "sender": {
                            "id": "1603594916368437"
                        },
                        "recipient": {
                            "id": "490985961270614"
                        },
                        "timestamp": 1509497461409,
                        "message": {
                            "mid": "mid.$cAAG-jMY5wb5lplSioVfdQ9TWivbN",
                            "seq": 228152,
                            "text": "hi"
                        }
                    }
                ]
            }
        ]
    }

class TestWebhook(unittest.TestCase):
    def setUp(self):
        """Define test variables and initialize app."""
        app = create_app(TestConfig)
        app.app_context().push()
        self.app = app.test_client()

    def test_api_can_get_webhook(self):
        """Test API can get webhook (GET request)."""
        res = self.app.get('/webhook')
        self.assertEqual(res.status_code, 403)

    # def test_api_post_to_webhook(self):
    #     """Test API can get webhook (GET request)."""
    #     res = self.app.post(
    #         '/webhook',
    #         data=json.dumps(generate_facebook_message()),
    #         content_type='application/json'
    #     )
    #     self.assertEqual(res.status_code, 200)

    def tearDown(self):
        """teardown all initialized variables."""
        pass

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
