import apiai
import json
from platobot.config import APIAIConfig

class APIAI(object):
    """
    api_ai related methods
    """
    def __init__(self):
        self.apiai = apiai.ApiAI(APIAIConfig.CLIENT_ACCESS_TOKEN)

    def get_user_intent(self, session_id, message_text):
        """Send message to apiai and get user intent"""
        request = self.apiai.text_request()
        request.session_id = session_id
        request.query = message_text
        apiai_response = json.loads(request.getresponse().read())
        result = apiai_response.get("result")
        return result
