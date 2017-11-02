import yaml
import os
from sqlalchemy.orm.attributes import flag_modified
from twilio.rest import Client

from platobot.surveys.survey_manager import SurveyManager
from platobot.config import TwilioConfig


class SMSSurveyManager(SurveyManager):

    def __init__(self):
        self.generic_survey_fields = yaml.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                 "sms/generic.yaml")))
        self.complete_msg = 'Report completed.'

    def send_response_to_user(self, survey_record):
        try:
            survey_record.state += 1
            response = survey_record.survey["fields"][survey_record.state]["text"]
        except IndexError:
            survey_record.state = -1
            response = self.complete_msg
        finally:
            self.send_response(survey_record.user, response)

    def get_survey_specs(self):
        return yaml.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "sms/earthquake.yaml")))

    def get_generic_survey_fields(self):
        return self.generic_survey_fields

    def send_response(self, user_number, response):
        """
        Have the bot reply to user
        """
        client = Client(TwilioConfig.ACCOUNT_SID, TwilioConfig.AUTH_TOKEN)

        client.api.account.messages.create(
            to=user_number,
            from_=TwilioConfig.NUMBER,
            body=response)
