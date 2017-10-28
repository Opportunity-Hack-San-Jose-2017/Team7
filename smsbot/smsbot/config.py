"""
All config lives here.

"""
import logging
import os

from smsbot.utils import database


# Logging configs
SQLALCHEMY_LOG_LEVEL = logging.ERROR


# Database Configs

class DevConfig(database.DBConfig):
    _config = {
        'dialect': 'mysql',
        'driver': 'pymysql',
        'username': 'root',
        'password': 'root',
        'host': 'localhost',
        'port': '3306',
        'database': 'smsbot',
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
        'database': 'smsbot',
        'charset': 'utf8mb4'
    }


DATABASE_CONFIG = DevConfig
