import logging
import datetime
import sqlalchemy
import json
from platobot.constants import Channels, SessionConfig
from platobot import models
from platobot.services.facebook_messenger import FacebookMessenger
from platobot.services.api_ai import APIAI

db_interface = models.platobot_db

log = logging.getLogger(__name__)

class Action(object):
    def __init__(self, action, suggested_reply):
        self.action = action
        self.suggested_reply = suggested_reply

# TODO: grab this from org info n stuff
bot_intro = {
    "text": "Hi, I'm Plato bot. I work for Ushahidi. I can help you send a report or tell you about Ushahidi.",
    "quick_replies": [
        {
            "content_type": "text",
            "title": "Send a report",
            "payload": "ask_to_send_report"
        },
        {
            "content_type": "text",
            "title": "About Ushahidi",
            "payload": "ushahidi_intro"
        }
    ]
}

bot_intro_skills = {
    "text": "I can help you send a report or tell you about Ushahidi.",
    "quick_replies": [{
        "content_type": "text",
        "title": "Send a report",
        "payload": "ask_to_send_report"
    }]
}

when_bot_is_confused = {
    "text": "Sorry. I don't quite understand that. But here are things I can do",
    "quick_replies": [{
        "content_type": "text",
        "title": "Send a report",
        "payload": "ask_to_send_report"
    }]
}

class BotController:
    def __init__(self):
        self.facebook_messenger = FacebookMessenger()
        self.apiai = APIAI()

    def reply(self, messaging_event, request_time):
        # the facebook ID of the person sending you the message
        sender_id = messaging_event["sender"]["id"]
        # the recipient's ID, which should be your page's facebook ID
        recipient_id = messaging_event["recipient"]["id"]
        # the message's text

        message = messaging_event["message"]
        # TODO: clean up this hacky code...
        message_text = message.get("text", '')
        if not message_text:
            attachments = message.get("attachments")
            if attachments:
                payload = attachments[0].get("payload")
                if payload:
                    coordinates = payload.get('coordinates')
                    if coordinates:
                        message_text = "latitude: {}, longitude: {}".format(coordinates.get('lat', ''),
                                                                            coordinates.get('long', ''))

        # return start_survey_flow(sender_id, recipient_id, message_text, request_time)
        action = self.get_user_intent_with_suggested_reply(messaging_event)
        log.info("Bot action %s", action.action)
        if action is not None:
            if action.action == "smalltalk.confirmation.cancel":
                return self.cancel_survey_flow(sender_id, recipient_id, message_text, request_time)
            elif self.is_in_middle_of_survey(messaging_event):
                return self.start_survey_flow(sender_id, recipient_id, message_text, request_time)
            elif action.action == "reports.want_to_send":
                return self.start_survey_flow(sender_id, recipient_id, message_text, request_time)
            elif action.action == "what_can_you_do" or action.action == "smalltalk.agent.answer_my_question":
                action.suggested_reply = bot_intro_skills
                return self.facebook_messenger.send_response(sender_id, action.suggested_reply)
            else:
                if not action.suggested_reply.get("text"):
                    action.suggested_reply = when_bot_is_confused
                return self.facebook_messenger.send_response(sender_id, action.suggested_reply)
        return self.facebook_messenger.send_response(sender_id, self.bot_fall_back_action().suggested_reply)

    def get_user_intent_with_suggested_reply(self, messaging_event):
        sender_id = messaging_event["sender"]["id"]
        message = messaging_event["message"]
        message_text = message.get("text", '')
        message_nlp = message.get("nlp")
        log.info("Get user intent from facebook wit ai")
        intent = self.get_user_intent_from_fb_wit_ai(message_text, message_nlp);
        if intent is None:
            log.info("Nothing to use from wit.ai, consulting apiai...")
            intent = self.get_user_intent_from_apiai(sender_id, message_text)
        log.info(intent)
        return intent

    def get_user_intent_from_fb_wit_ai(self, message_text, message_nlp):
        if message_nlp is not None:
            entities = message_nlp.get("entities")
            if entities is None:
                return None
            if self.has_greetings(entities):
                return Action("greetings", bot_intro)
        return None

    def has_greetings(self, entities):
        greetings = entities.get("greetings")
        if greetings is not None and greetings[0] is not None:
            if greetings[0]["confidence"] > 0.9:
                return True
        return False

    def get_user_intent_from_apiai(self, session_id, message_text):
        result = self.apiai.get_user_intent(session_id, message_text)
        if result is None:
            return self.bot_fall_back_action()

        action = result.get("action")
        speech = result['fulfillment']['speech']

        return Action(action, {"text": speech})

    def bot_fall_back_action(self):
        return Action(None, when_bot_is_confused)

    def is_in_middle_of_survey(self, messaging_event):
        sender_id = messaging_event["sender"]["id"]
        session = db_interface.new_session()
        record = session.query(models.Survey).filter(
            models.Survey.user == sender_id,
            models.Survey.state != -1
            ).order_by(sqlalchemy.desc(models.Survey.message_submission_time)).first()
        session.close()
        if record is None:
            return False

        return True

    def cancel_survey_flow(self, sender_id, recipient_id, message_text, request_time):
        pass

    def start_survey_flow(self, sender_id, recipient_id, message_text, request_time):
        self.save_user_message(sender_id, Channels.FACEBOOK, message_text, request_time)

    def save_user_message(self, user, channel, user_message, user_message_time):
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

