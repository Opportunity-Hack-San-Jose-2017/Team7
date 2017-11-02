import unittest
import os
import json
from platobot.chat.chat_flow_manager import get_reply_message

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

class ChatFlowTestCases(unittest.TestCase):
    def setUp(self):
        self.greetings = generate_greeting_intent()
        pass

    def test_reply_to_greetings(self):
        response = get_reply_message(self.greetings)
        self.assertDictEqual(response, {
            "text": "Hi, I'm Plato bot. Here are things I can do.",
            "quick_replies": [{
                "content_type": "text",
                "title": "Send a report",
                "payload": "ask_to_send_report"
            }]
        })

    def tearDown(self):
        pass

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
