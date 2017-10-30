import yaml
import os

from platobot.surveys.survey_manager import SurveyManager


class FacebookSurveyManager(SurveyManager):

    def __init__(self):
        self.generic_survey_fields = yaml.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                 "facebook/generic.yaml")))
        self.complete_msg = {"text": "Report completed!"}

    def get_response_to_user(self, survey_record):
        try:
            survey_record.state += 1
            return survey_record.survey["fields"][survey_record.state]
        except IndexError:
            survey_record.state = -1
            return self.complete_msg

    def get_survey_specs(self):
        return yaml.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "facebook/violence.yaml")))

    def get_generic_survey_fields(self):
        return self.generic_survey_fields
