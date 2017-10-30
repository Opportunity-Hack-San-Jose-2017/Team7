import abc
from sqlalchemy.orm.attributes import flag_modified


class SurveyManager(abc.ABC):

    def record_user_response(self, survey_record, user_input_msg, user_submission_time):
        """
        update user's response in db, update state of survey completion, and pull in new questions once we
        identify the survey template to use
        :param survey_record: survey from database
        :param user_input_msg: message from user
        :param user_submission_time: time we received message from user
        :return: None
        """
        state = survey_record.state

        if state == 0:
            self.init_survey(survey_record)
        elif state == len(self.get_generic_survey_fields()) - 1:
            survey_record.survey["fields"].extend(self.get_survey_specs())
            # using this since json column is not updated with sqlalchemy
            flag_modified(survey_record, "survey")

        survey_record.survey["fields"][state]["data"] = user_input_msg
        survey_record.survey["fields"][state]["submission_time"] = user_submission_time

        survey_record.submission_time = user_submission_time
        return

    def init_survey(self, survey_record):
        """ Input initial generic survey questions, in order to find out which survey template to use later on """
        survey_record.survey = {"fields": self.get_generic_survey_fields()}
        return

    @abc.abstractmethod
    def get_survey_specs(self):
        return {}

    @abc.abstractmethod
    def get_generic_survey_fields(self):
        return []

    @abc.abstractmethod
    def get_response_to_user(self, survey_record):
        return []
