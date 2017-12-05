import logging

import sqlalchemy as db

from platobot import config
from platobot.utils import database


logging.getLogger('sqlalchemy.engine').setLevel(config.SQLALCHEMY_LOG_LEVEL)
print('setting database config');
platobot_db = database.DBInterface(db_config=config.DATABASE_CONFIG())


# Models


class Survey(platobot_db.BASE_MODEL):
    """
    This table stores survey data received from user
    """
    __tablename__ = 'survey'

    user = db.Column(db.String(100))
    channel = db.Column(db.String(20))
    survey = db.Column(database.JSONEncodedDict)
    state = db.Column(db.Integer)
    # post id from Ushahidi
    post_id = db.Column(db.Integer)
    form_name = db.Column(db.String(100))
    creation_time = db.Column(db.DateTime)
    unprocessed_user_message = db.Column(db.String(140))
    message_submission_time = db.Column(db.DateTime)
