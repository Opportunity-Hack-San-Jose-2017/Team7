"""
This module handles the database bootstrap. All the database config, bootstrap data insertions, etc should be done here.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..'))
from platobot.utils import database
from platobot import config, models


if __name__ == '__main__':
    database.DBInterface.create_database(config.DATABASE_CONFIG(), delete_existing=True)
    models.platobot_db.bootstrap_db(delete_existing=True)
    models.platobot_db.curate_database_encoding_to_utf8()
