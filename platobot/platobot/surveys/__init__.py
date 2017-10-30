from platobot.surveys.sms_survey_manager import SMSSurveyManager
from platobot.surveys.facebook_survey_manager import FacebookSurveyManager
from platobot.constants import Channels


def get_survey_manager(channel):
    if channel == Channels.SMS:
        return SMSSurveyManager()
    elif channel == Channels.FACEBOOK:
        return FacebookSurveyManager()