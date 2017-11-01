import yaml
import os
import logging

from platobot.surveys.survey_manager import SurveyManager
from platobot.utils.facebook_api import send_response

log = logging.getLogger(__name__)

class FacebookSurveyManager(SurveyManager):

    def __init__(self):
        self.generic_survey_fields = yaml.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                 "facebook/generic.yaml")))
        self.complete_msg = {"text": "Report completed!"}

    def send_response_to_user(self, survey_record):
        try:
            survey_record.state += 1
            response = survey_record.survey["fields"][survey_record.state]
        except IndexError:
            survey_record.state = -1
            response = self.complete_msg
        finally:
            send_response(survey_record.user, response)

    def get_survey_specs(self):
        return yaml.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "facebook/violence.yaml")))

    def get_generic_survey_fields(self):
        return self.generic_survey_fields

