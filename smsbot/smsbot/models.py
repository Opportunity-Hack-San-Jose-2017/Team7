import logging

import sqlalchemy as db

from smsbot import config
from smsbot.utils import database

logging.getLogger('sqlalchemy.engine').setLevel(config.SQLALCHEMY_LOG_LEVEL)
smsbot_db = database.DBInterface(db_config=config.DATABASE_CONFIG())


# Models


class Repository(smsbot.BASE_MODEL):
    """
    This table stores repository objects, where each record represents an actual git repository.
    """
    __tablename__ = 'repository'

    name = db.Column(db.String(100))
    git_url = db.Column(db.String(200))
