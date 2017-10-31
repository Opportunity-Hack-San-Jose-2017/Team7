"""
Main entry
"""
import logging
import json
import datetime
import sys
import os
from os.path import join, dirname
import requests
from dotenv import load_dotenv

from flask import Flask, request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..'))
from platobot.session_management import session_manager
from platobot.constants import Channels

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

log = logging.getLogger(__name__)


app = Flask(__name__)


class FacebookConfig:

    USHAHIDI_API = 'http://35.203.151.94/platform/api/v3'
    USHAHIDI_TOKEN = 'Bearer jWPuTIaLPoVBNgLd1kf96m0Q78H12JhCPSmeCswJ'
    FACEBOOK_MESSAGEING_API = 'https://graph.facebook.com/v2.6/me/messages'
    VERIFY_TOKEN = 'moo'
    PAGE_ACCESS_TOKEN = 'EAARCCMNIDsQBAIqhyLHcQ2OaJlJtlXQgeDiug3Itk9HAYeZASZBhygKQ8SNf3ZC67wQ2vYqVg7zKErCCCvapLeShB6vD1c0gyNZBl1MLbFvItYcos6UwFZAKTBeaqcdpNMDoiYZCmASZAZCstCawyaUweZBKK1usFKhDCuUYnJ7e9QQZDZD'
    # PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")

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
        log.info(r.status_code)
        log.info(r.text)


@app.route('/webhook', methods=['GET'])
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


@app.route('/webhook', methods=['POST'])
def facebook_webhook():
    """
    Endpoint for processing incoming messaging events
    """
    request_time = datetime.datetime.utcnow()
    data = request.get_json()
    log.debug(data)

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    # the facebook ID of the person sending you the message
                    sender_id = messaging_event["sender"]["id"]
                    # the recipient's ID, which should be your page's facebook ID
                    recipient_id = messaging_event["recipient"]["id"]
                    # the message's text
                    message_text = messaging_event["message"].get("text")

                    response = session_manager.handle_user_input(sender_id, Channels.FACEBOOK,
                                                                 message_text, request_time)

                    send_response(sender_id, response)

                # delivery confirmation
                if messaging_event.get("delivery"):
                    pass

                # optin confirmation
                if messaging_event.get("optin"):
                    pass

                # user clicked/tapped "postback" button in earlier message
                if messaging_event.get("postback"):
                    pass

    return "ok", 200


if __name__ == '__main__':
    app.run(debug=True)
