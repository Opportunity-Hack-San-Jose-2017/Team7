import logging
import json
import requests

from platobot.config import FacebookConfig

log = logging.getLogger(__name__)

def send_response(recipient_id, response):
    """
    Have the bot reply to user
    """

    log.info("sending message to {recipient}: {text}".format(recipient=recipient_id, text=response["text"]))

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
        "message": response
    })
    r = requests.post(FacebookConfig.FACEBOOK_MESSAGEING_API, params=params, headers=headers, data=data)
    if r.status_code != 200:
        log.error(r.status_code)
        log.error(r.text)

