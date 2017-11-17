"""
webhooks
"""
import logging
import json
import datetime
import sys
import os

from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse

# sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..'))
from platobot.config import FacebookConfig, UshahidiConfig
from platobot.chat.chat_flow_manager import ChatFlowManager
from platobot.constants import Channels

chat_flow_manager = ChatFlowManager()
webhook = Blueprint('webhook', __name__)

logging.basicConfig(stream=sys.stdout,
    format='%(asctime)s|%(levelname)s|%(filename)s:%(lineno)s|%(message)s',
    level=logging.DEBUG)

@webhook.route('/webhook', methods=['GET'])
def facebook_verify():
    """
    When the endpoint is registered as a webhook, it must echo back
    the 'hub.challenge' value it receives in the query arguments
    """
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == FacebookConfig.VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Unable to verify", 403 

@webhook.route('/webhook', methods=['POST'])
def facebook_webhook():
    """
    Endpoint for processing incoming messaging events
    """
    request_time = datetime.datetime.utcnow()
    data = request.get_json()
    print(data)

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message
                    chat_flow_manager.reply(messaging_event, request_time)

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

@webhook.route('/inbound', methods=['GET', 'POST'])
def twilio_inbound_webhook():
    """."""
    from_number = request.values.get('From', '')
    message_received = request.values.get('Body', '')

    chat_flow_manager.save_user_message(from_number, Channels.SMS, message_received, datetime.datetime.utcnow())

    # resp = MessagingResponse()
    # resp.message("{}, thanks for the message: {} !".format(from_number, message_received))
    return "ok", 200
