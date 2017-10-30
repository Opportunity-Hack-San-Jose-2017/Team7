from platobot.constants import Channels
from platobot.message import sms_message


def message_callback(channel, **kwargs):
    if channel == Channels.SMS:
        return sms_message.message_callback(**kwargs)

