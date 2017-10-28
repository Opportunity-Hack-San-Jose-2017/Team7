"""
This module handles the database bootstrap. All the database config, bootstrap data insertions, etc should be done here.
"""


from smsbot.utils import database
from smsbot import models, config


if __name__ == '__main__':
    database.DBInterface.create_database(config.DATABASE_CONFIG(), delete_existing=True)
    smsbot.smsbot_db.bootstrap_db(delete_existing=True)
    smsbot.smsbot_db.curate_database_encoding_to_utf8()
