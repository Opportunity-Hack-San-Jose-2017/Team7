import logging
import json
import requests

from platobot.config import FacebookConfig

log = logging.getLogger(__name__)

class FacebookMessenger:
    def send_response(self, recipient_id, response):
        """
        Have the bot reply to user
        """

        log.info("sending message to {recipient}: {text}".format(recipient=recipient_id, text=response["text"]))

        # since I'm adding extra values to the response in  facebook survey manager....
        # and facebook only wants {text, quick_replies}
        formatted_res = {}
        formatted_res['text'] = response.get('text')
        if response.get('quick_replies') is not None and len(response.get('quick_replies')) != 0:
            formatted_res['quick_replies'] = response.get('quick_replies')

        params = {
            "access_token": FacebookConfig.PAGE_ACCESS_TOKEN
        }
        headers = {
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "recipient": {
                "id": recipient_id
            },
            "message": formatted_res
        })
        r = requests.post(FacebookConfig.FACEBOOK_MESSAGEING_API, params=params, headers=headers, data=data)
        if r.status_code != 200:
            log.error(r.status_code)
            log.error(r.text)

