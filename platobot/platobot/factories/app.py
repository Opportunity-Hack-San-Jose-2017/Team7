"""
To create app
"""
import logging
import sys

from flask import Flask
from platobot.routes.webhook import webhook
from platobot.utils import database
from platobot import models

def create_app(config):
    """ application factory pattern to make it easy to test
        http://flask.pocoo.org/docs/0.12/patterns/appfactories/
    """
    app = Flask(__name__)
    log = logging.getLogger(__name__)
    app.config.from_object(config)

    register_blueprints(app)

    logging.basicConfig(stream=sys.stdout,
        format='%(asctime)s|%(levelname)s|%(filename)s:%(lineno)s|%(message)s',
        level=logging.DEBUG)

    return app

def reinit_db(config):
    """ To switch to different db based on the config """
    models.platobot_db.db_config = config
    models.platobot_db.db_url = config.get_uri()
    models.platobot_db.reinit_engine()
    models.platobot_db.create_database(config)
    models.platobot_db.create_tables(delete_existing=True)
    models.platobot_db.curate_database_encoding_to_utf8()
    return models.platobot_db

def register_blueprints(app):
    """ register all the blueprints here """
    app.register_blueprint(webhook)

    return None

