"""
To create app
"""
import logging
import json
import datetime
import sys
import os

from flask import Flask
from platobot.routes.webhook import webhook

def create_app(config):
    app = Flask(__name__)
    log = logging.getLogger(__name__)
    app.config.from_object(config)

    register_blueprints(app)

    logging.basicConfig(stream=sys.stdout,
        format='%(asctime)s|%(levelname)s|%(filename)s:%(lineno)s|%(message)s',
        level=logging.DEBUG)

    return app

def register_blueprints(app):
    app.register_blueprint(webhook)

    return None

