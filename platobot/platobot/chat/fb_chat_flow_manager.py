import datetime
import sqlalchemy
from platobot.constants import Channels, SessionConfig
from platobot import models
from platobot.utils.facebook_api import send_response

db_interface = models.platobot_db

# TODO: grab this from org info n stuff
bot_intro = {
    "text": "Hi, I'm Plato bot. Here are things I can do.",
    "quick_replies": [{
        "content_type": "text",
        "title": "Send a report",
        "payload": "ask_to_send_report"
    }]
}

# TODO: make this into a class??

def reply(messaging_event, request_time):
    # the facebook ID of the person sending you the message
    sender_id = messaging_event["sender"]["id"]
    # the recipient's ID, which should be your page's facebook ID
    recipient_id = messaging_event["recipient"]["id"]
    # the message's text

    message = messaging_event["message"]
    # TO DO: get different vals for different types of user input
    message_text = message.get("text", '')

    response = get_reply_message(messaging_event);
    if response is None:
        return start_survey_flow(sender_id, recipient_id, message_text, request_time)
    else:
        send_response(sender_id, response)

def get_reply_message(messaging_event):
    message = messaging_event["message"]
    # TO DO: get different vals for different types of user input
    message_text = message.get("text", '')
    message_nlp = message.get("nlp")
    if message_nlp is not None:
        entities = message_nlp.get("entities")
        if hasGreetings(entities):
            return reply_to_greetings()
    return None

def hasGreetings(entities):
    greetings = entities.get("greetings")
    if greetings is not None and greetings[0] is not None:
        if greetings[0]["confidence"] > 0.9:
            return True
    return False

def reply_to_greetings():
    return bot_intro

def smalltalk():
    pass

def start_survey_flow(sender_id, recipient_id, message_text, request_time):
    save_user_message(sender_id, Channels.FACEBOOK, message_text, request_time)
    # response = session_manager.handle_user_input(sender_id, Channels.FACEBOOK,
    #                                             message_text, request_time)

    # send_response(sender_id, response)


def save_user_message(user, channel, user_message, user_message_time):
    session = db_interface.new_session()
    record = session.query(models.Survey).filter(models.Survey.user == user,
                                                    models.Survey.channel == channel).order_by(
        sqlalchemy.desc(models.Survey.message_submission_time)).first()

    if not record or record.state < 0 or \
                            datetime.datetime.utcnow() - record.message_submission_time > datetime.timedelta(
                seconds=SessionConfig.TIMEOUT):
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

