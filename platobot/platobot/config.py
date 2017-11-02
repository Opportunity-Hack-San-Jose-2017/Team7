"""
All config lives here.

"""
import logging
import os

from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
from platobot.utils import database

# Logging configs
SQLALCHEMY_LOG_LEVEL = logging.ERROR


# Database Configs

class TestConfig(database.DBConfig):
    _config = {
        'dialect': 'mysql',
        'driver': 'pymysql',
        'username': 'root',
        'password': 'root',
        'host': 'localhost',
        'port': '3306',
        'database': 'platobottest',
        'charset': 'utf8mb4'
    }

class DevConfig(database.DBConfig):
    _config = {
        'dialect': 'mysql',
        'driver': 'pymysql',
        'username': 'root',
        'password': 'root',
        'host': 'localhost',
        'port': '3306',
        'database': 'platobot',
        'charset': 'utf8mb4'
    }


class ProdConfig(database.DBConfig):
    """
    TODO: Update Prod database info from AWS
    """
    _config = {
        'dialect': 'mysql',
        'driver': 'pymysql',
        'username': 'root',
        'password': '',
        'host': 'localhost',
        'port': '3306',
        'database': 'platobot',
        'charset': 'utf8mb4'
    }


DATABASE_CONFIG = DevConfig


# Configs
class FacebookConfig:
    FACEBOOK_MESSAGEING_API = 'https://graph.facebook.com/v2.6/me/messages'
    VERIFY_TOKEN = 'moo'
    # PAGE_ACCESS_TOKEN = 'EAARCCMNIDsQBAIqhyLHcQ2OaJlJtlXQgeDiug3Itk9HAYeZASZBhygKQ8SNf3ZC67wQ2vYqVg7zKErCCCvapLeShB6vD1c0gyNZBl1MLbFvItYcos6UwFZAKTBeaqcdpNMDoiYZCmASZAZCstCawyaUweZBKK1usFKhDCuUYnJ7e9QQZDZD'
    PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")


class UshahidiConfig:
    USHAHIDI_API = 'http://35.203.151.94/platform/api/v3'
    # token expired
    USHAHIDI_TOKEN = 'Bearer jWPuTIaLPoVBNgLd1kf96m0Q78H12JhCPSmeCswJ'


class APIAIConfig:
    # CLIENT_ACCESS_TOKEN = '9d5b69f4c2504d298b7a4331ad6c9644'
    CLIENT_ACCESS_TOKEN = os.environ.get("APIAI_CLIENT_ACCESS_TOKEN")


class TwilioConfig:
    ACCOUNT_SID = 'ACcc1ea4a766dad380e75e8a053fbb7585'
    AUTH_TOKEN = '8054e1a09e67e381256bcbbd2a4a55b5'
    NUMBER = '+16288000053'
