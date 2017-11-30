import unittest
import os
import json
from platobot.controllers.bot_controller import BotController
from platobot.test.test_main import BaseTestCase

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
    # def setUp(self):
    #     self.greetings = generate_greeting_intent()

    def test_reply_to_greetings(self):
        print(self.app)
        # response = get_reply_message(self.greetings)
        # self.assertDictEqual(response, {
        #     "text": "Hi, I'm Plato bot. Here are things I can do.",
        #     "quick_replies": [{
        #         "content_type": "text",
        #         "title": "Send a report",
        #         "payload": "ask_to_send_report"
        #     }]
        # })
        pass
