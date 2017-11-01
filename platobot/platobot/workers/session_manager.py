import datetime
import sqlalchemy

from platobot import models
from platobot.surveys import get_survey_manager
from platobot.constants import SessionConfig
db_interface = models.platobot_db


def handle_user_input(user, channel, user_input_msg, user_submission_time):
    """
    Singleton session manager handles user input, for now
    :param user: user contact, either phone number or facebook id
    :param channel: as defined in platobot.constants.Channels
    :param user_input_msg: message string from user
    :param user_submission_time: time we received message from user
    :return: response to user
    """
    session = db_interface.new_session()
    record = session.query(models.Survey).filter(models.Survey.user == user,
                                                 models.Survey.channel == channel
                                                 ).order_by(sqlalchemy.desc(models.Survey.message_submission_time)).first()

    if not record or record.state < 0 or datetime.datetime.utcnow() - user_submission_time > datetime.timedelta(seconds=SessionConfig.TIMEOUT):
        print("add new record")
        record = models.Survey(user=user, channel=channel, state=0, creation_time=datetime.datetime.utcnow())
        session.add(record)

    survey_manager = get_survey_manager(channel)

    record.unprocessed_user_message = user_input_msg

    survey_manager.record_user_response(record, user_input_msg, user_submission_time)
    response = survey_manager.send_response_to_user(record)

    session.commit()
    session.close()
    return response
