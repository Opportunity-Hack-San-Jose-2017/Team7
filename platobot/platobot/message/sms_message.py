import datetime
from platobot.constants import Channels
from platobot.session_management import session_manager
"""
from test import sms_user


def send_message(user_number, msg):
    sms_user.receive_message(user_number, msg)
    return
"""


def message_callback(user_number='', msg=''):
    reply = session_manager.handle_user_input(user_number, Channels.SMS, msg, datetime.datetime.utcnow())
    return reply
