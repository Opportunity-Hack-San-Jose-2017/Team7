import os
import json
import datetime
from unittest.mock import patch, ANY
from platobot.controllers.bot_controller import BotController
from platobot.test.test_main import BaseTestCase
from platobot.services import api_ai
from platobot.services import facebook_messenger

def generate_greeting_intent():
    return {
        "sender": {
            "id": "1668875906520127"
        },
        "recipient": {
            "id": "564363103905538"
        },
        "timestamp": 1509554514675,
        "message": {
            "mid": "mid.$cAAIBSVOjS-plqbsy81feHXmsvNpp",
            "seq": 228446,
            "text": "hi",
            "nlp": {
                "entities": {
                    "location": [
                        {
                            "suggested": True,
                            "confidence": 0.87836,
                            "value": "hi",
                            "type": "value"
                        }
                    ],
                    "greetings": [
                        {
                            "confidence": 0.99993050098374,
                            "value": "true"
                        }
                    ]
                }
            }
        }
    }

class BotControllerTestCases(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.greetings = generate_greeting_intent()
        self.bot_controller = BotController()

    # @patch('platobot.services.api_ai.APIAI.get_user_intent')
    @patch('platobot.services.facebook_messenger.FacebookMessenger.send_response')
    def test_reply_to_greetings(self, send_response):
        """ Introduces self when see greetings intent """
        self.bot_controller.reply(self.greetings, datetime.datetime.utcnow())
        send_response.assert_called_once_with(self.greetings["sender"]["id"],
        {
            "text": "Hi, I'm Plato bot. I work for Ushahidi. I can help you send a report or tell you about Ushahidi.",
            "quick_replies": [
                {
                    "content_type": "text",
                    "title": "Send a report",
                    "payload": "ask_to_send_report"
                },
                {
                    "content_type": "text",
                    "title": "About Ushahidi",
                    "payload": "ushahidi_intro"
                }
            ]
        })
