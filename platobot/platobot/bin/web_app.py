import logging
import datetime

from flask import Flask, request
import sqlalchemy

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..'))
# from platobot.workers import session_manager
from platobot.constants import Channels, SessionConfig
from platobot.config import FacebookConfig
from platobot import models

db_interface = models.platobot_db

log = logging.getLogger(__name__)


app = Flask(__name__)


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
                    print(messaging_event["message"])
                    message_text = messaging_event["message"].get("text", '')

                    save_user_message(sender_id, Channels.FACEBOOK, message_text, request_time)
                    # response = session_manager.handle_user_input(sender_id, Channels.FACEBOOK,
                    #                                             message_text, request_time)

                    # send_response(sender_id, response)

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


def save_user_message(user, channel, user_message, user_message_time):
    session = db_interface.new_session()
    record = session.query(models.Survey).filter(models.Survey.user == user,
                                                 models.Survey.channel == channel).order_by(
        sqlalchemy.desc(models.Survey.message_submission_time)).first()

    if not record or record.state < 0 or \
       datetime.datetime.utcnow() - record.message_submission_time > datetime.timedelta(seconds=SessionConfig.TIMEOUT):
        record = models.Survey(user=user, channel=channel, state=0,
                               creation_time=datetime.datetime.utcnow(),
                               unprocessed_user_message=user_message,
                               message_submission_time=user_message_time)
        session.add(record)
    else:
        record.unprocessed_user_message = user_message
        record.message_submission_time = user_message_time

    session.commit()
    return record.id


if __name__ == '__main__':
    app.run(debug=True)
