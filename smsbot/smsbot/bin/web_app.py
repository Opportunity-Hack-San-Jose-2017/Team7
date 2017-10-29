import logging
import os
import sys
import json
from datetime import datetime

import requests
from flask import Flask, request


log = logging.getLogger(__name__)


app = Flask(__name__)


class FacebookConfig:

    FACEBOOK_MESSAGEING_API = 'https://graph.facebook.com/v2.6/me/messages'
    VERIFY_TOKEN = 'moo'
    PAGE_ACCESS_TOKEN = 'EAARCCMNIDsQBAIqhyLHcQ2OaJlJtlXQgeDiug3Itk9HAYeZASZBhygKQ8SNf3ZC67wQ2vYqVg7zKErCCCvapLeShB6vD1c0gyNZBl1MLbFvItYcos6UwFZAKTBeaqcdpNMDoiYZCmASZAZCstCawyaUweZBKK1usFKhDCuUYnJ7e9QQZDZD'


def send_message(recipient_id, message_text):

    log.info("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

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
        "message": {
            "text": message_text
        }
    })
    r = requests.post(FacebookConfig.FACEBOOK_MESSAGEING_API, params=params, headers=headers, data=data)
    if r.status_code != 200:
        log.info(r.status_code)
        log.info(r.text)


@app.route('/', methods=['GET'])
def facebook_verify():
    """
    When the endpoint is registered as a webhook, it must echo back
    the 'hub.challenge' value it receives in the query arguments
    """

    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == FacebookConfig.VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def facebook_webhook():
    """
    Endpoint for processing incoming messaging events
    """
    data = request.get_json()
    log.debug(data)

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    send_message(sender_id, "roger that!")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


if __name__ == '__main__':
    app.run(debug=True)
