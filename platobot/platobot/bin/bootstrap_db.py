"""
This module handles the database bootstrap. All the database config, bootstrap data insertions, etc should be done here.
"""

from platobot.utils import database
from platobot import config, models


if __name__ == '__main__':
    database.DBInterface.create_database(config.DATABASE_CONFIG(), delete_existing=True)
    models.platobot_db.bootstrap_db(delete_existing=True)
    models.platobot_db.curate_database_encoding_to_utf8()
