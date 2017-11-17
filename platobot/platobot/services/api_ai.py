import apiai
from platobot.config import APIAIConfig

class APIAI:
    def __init__(self):
        self.ai = apiai.ApiAI(APIAIConfig.CLIENT_ACCESS_TOKEN)

    def get_user_intent(self, session_id, message_text):
        request = ai.text_request()
        request.session_id = session_id
        request.query = message_text
        apiai_response = json.loads(request.getresponse().read())
        result = apiai_response.get("result")
        return result

