import requests
import json
from unittest.mock import patch, ANY
from platobot.config import FacebookConfig
from platobot.test.test_main import BaseTestCase
from platobot.controllers.bot_controller import BotController

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

class TestWebhook(BaseTestCase):
    def test_get_webhook_denied(self):
        """Get denied if provided incorrect info."""
        res = self.client.get("/webhook")
        self.assertEqual(res.status_code, 403)

    def test_get_webhook_ok(self):
        """Can get webhook (GET request)."""
        res = self.client.get("/webhook?hub.verify_token=moo&hub.challenge=CHALLENGE_ACCEPTED&hub.mode=subscribe")
        self.assertStatus(res, 200)
        self.assertResponseText(res, b'CHALLENGE_ACCEPTED')

    @patch('platobot.controllers.bot_controller.BotController.reply')
    def test_facebook_post_message_event_to_webhook(self, bot_reply_mock):
        """Test API can get webhook (GET request)."""
        bot_reply_mock.return_value = None
        facebook_message = generate_facebook_message()
        res = self.client.post(
            '/webhook',
            data=json.dumps(facebook_message),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        bot_reply_mock.assert_called_once_with(facebook_message["entry"][0]["messaging"][0], ANY)

