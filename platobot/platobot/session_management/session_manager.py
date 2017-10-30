import datetime
import sqlalchemy

from platobot import models
from platobot.surveys.survey_manager import SurveyManager
from platobot.constants import SessionConfig
db_interface = models.platobot_db


def handle_user_input(user, channel, user_input_msg, user_submission_time):
    session = db_interface.new_session()
    record = session.query(models.Survey).filter(models.Survey.user == user,
                                                 models.Survey.channel == channel
                                                 ).order_by(sqlalchemy.desc(models.Survey.submission_time)).first()

    if not record or record.state < 0 or datetime.datetime.utcnow() - record.submission_time > datetime.timedelta(seconds=SessionConfig.max_interval):
        record = models.Survey(user=user, channel=channel, state=0, creation_time=datetime.datetime.utcnow())
        session.add(record)

    SurveyManager.record_user_response(record, user_input_msg, user_submission_time)
    question = SurveyManager.get_next_question(record)

    # message.send_message(channel, user=user, msg=question)

    session.commit()
    session.close()
    return question






