import datetime
from platobot.constants import Channels
from platobot.session_management import session_manager


def message_callback(user_number='', msg=''):
    reply = session_manager.handle_user_input(user_number, Channels.SMS, msg, datetime.datetime.utcnow())
    return reply
