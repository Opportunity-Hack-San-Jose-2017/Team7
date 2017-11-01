import yaml
import os
from sqlalchemy.orm.attributes import flag_modified

from platobot.surveys.survey_manager import SurveyManager


class SMSSurveyManager(SurveyManager):

    def __init__(self):
        self.generic_survey_fields = yaml.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                 "sms/generic.yaml")))
        self.complete_msg = 'Report completed.'

    def send_response_to_user(self, survey_record):
        try:
            survey_record.state += 1
            return survey_record.survey["fields"][survey_record.state]["text"]
        except IndexError:
            survey_record.state = -1
            return self.complete_msg

    def get_survey_specs(self):
        return yaml.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "sms/earthquake.yaml")))

    def get_generic_survey_fields(self):
        return self.generic_survey_fields

    def record_user_response(self, survey_record, user_message, message_time):
        """
        This is temporary - before sms is hooked with twilio
        update user's response in db, update state of survey completion, and pull in new questions once we
        identify the survey template to use
        :param survey_record: survey from database
        :return: None
        """
        state = survey_record.state

        if state == 0:
            self.init_survey(survey_record)
        elif state == len(self.get_generic_survey_fields()) - 1:
            survey_record.survey["fields"].extend(self.get_survey_specs())
            # using this since json column is not updated with sqlalchemy
            flag_modified(survey_record, "survey")

        survey_record.survey["fields"][state]["data"] = user_message
        survey_record.survey["fields"][state]["submission_time"] = message_time

        survey_record.message_submission_time = message_time
        return