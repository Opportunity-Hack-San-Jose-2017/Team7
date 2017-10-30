import logging
import os
import sys
import json
from datetime import datetime

import requests
from flask import Flask, request

states = {}
log = logging.getLogger(__name__)


app = Flask(__name__)


class FacebookConfig:

    FACEBOOK_MESSAGEING_API = 'https://graph.facebook.com/v2.6/me/messages'
    VERIFY_TOKEN = 'moo'
    PAGE_ACCESS_TOKEN = 'EAARCCMNIDsQBAIqhyLHcQ2OaJlJtlXQgeDiug3Itk9HAYeZASZBhygKQ8SNf3ZC67wQ2vYqVg7zKErCCCvapLeShB6vD1c0gyNZBl1MLbFvItYcos6UwFZAKTBeaqcdpNMDoiYZCmASZAZCstCawyaUweZBKK1usFKhDCuUYnJ7e9QQZDZD'

def handle_message(sender_id, received_message):
    """
    Decide what to do with this msg
    """
    response = {
        "text": "I don't get it"
    }

    if sender_id in states:
        log.info("detected repeat user")
        states[sender_id] += 1
    else:
        log.info("detected new user")
        states[sender_id] = 1

    # if received_message.attachments and received_message.attachments[0].type == "location":
    #     log.info("detected location:" + received_message.attachments[0].payload)

    if states[sender_id] == 1:
        response = {
            "text": "Are you in immediate danger?",
            "quick_replies": [
                {
                    "content_type": "text",
                    "title": "Yes",
                    "payload": "reply1"
                },
                {
                    "content_type": "text",
                    "title": "No",
                    "payload": "reply2"
                }
            ]
        }
    elif states[sender_id] == 2:
        response = {
            "text": "What is your location?",
            "quick_replies": [
                {
                    "content_type":"location",
                    "title": "location",
                    "payload": "reply3"
                }
            ]
            }
    elif states[sender_id] == 3:
        response = {
            "text": "Select a category",
            "quick_replies": [
                {
                    "content_type": "text",
                    "title": "Violence",
                    "payload": "reply1"
                },
                {
                    "content_type": "text",
                    "title": "Harassment",
                    "payload": "reply2"
                },
                {
                    "content_type": "text",
                    "title": "Danger",
                    "payload": "reply3"
                },
                {
                    "content_type": "text",
                    "title": "Other",
                    "payload": "reply4"
                }
            ]
        }
    elif states[sender_id] == 4:
        response = {
            "text": "all done!"
        }

    send_response(sender_id, response)

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
                    message_text = messaging_event["message"]["text"]

                    handle_message(sender_id, message_text)

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
