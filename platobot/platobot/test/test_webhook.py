import json
from platobot.test.test_main import BaseTestCase

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

    def test_api_post_to_webhook(self):
        """Test API can get webhook (GET request)."""
        res = self.client.post(
            '/webhook',
            data=json.dumps(generate_facebook_message()),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)

