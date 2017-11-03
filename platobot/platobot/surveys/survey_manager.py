import abc
from sqlalchemy.orm.attributes import flag_modified
import logging
log = logging.getLogger(__name__)


class SurveyManager(abc.ABC):

    def record_user_response(self, survey_record):
        """
        update user's response in db, update state of survey completion, and pull in new questions once we
        identify the survey template to use
        :param survey_record: survey from database
        :return: None
        """
        state = survey_record.state

        if state == 0:
            self.init_survey(survey_record)

        log.info(len(self.get_generic_survey_fields()) - 1)
        log.info(state)
        if state == len(self.get_generic_survey_fields()) - 1:
            survey_record.survey["fields"].extend(self.get_survey_specs(survey_record))

        survey_record.survey["fields"][state]["data"] = survey_record.unprocessed_user_message
        survey_record.survey["fields"][state]["submission_time"] = survey_record.message_submission_time
        # using this since json column is not updated with sqlalchemy
        flag_modified(survey_record, "survey")

        survey_record.message_submission_time = survey_record.message_submission_time
        survey_record.unprocessed_user_message = None
        return

    def init_survey(self, survey_record):
        """ Input initial generic survey questions, in order to find out which survey template to use later on """
        survey_record.survey = {"fields": self.get_generic_survey_fields()}
        return

    @abc.abstractmethod
    def init_generic_survey(self):
        """this won't be used anymore since we are getting survey from Ushahidi"""
        return

    @abc.abstractmethod
    def get_survey_specs(self, survey_record):
        """this won't be used anymore since we are getting survey from Ushahidi"""
        return {}

    @abc.abstractmethod
    def get_generic_survey_fields(self):
        return []

    @abc.abstractmethod
    def send_response_to_user(self, survey_record):
        return []
