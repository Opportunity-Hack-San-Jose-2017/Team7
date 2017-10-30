import yaml
import os

from sqlalchemy.orm.attributes import flag_modified


class SurveyManager(object):
    generic_survey_fields = yaml.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "generic.yaml")))
    complete_msg = 'Report completed.'

    @classmethod
    def record_user_response(cls, survey_record, user_input_msg, user_submission_time):
        state = survey_record.state

        if state == 0:
            cls.init_survey(survey_record)
        elif state == len(cls.generic_survey_fields) - 1:
            survey_record.survey["fields"].extend(cls.get_survey_specs())
            # using this since json column is not updated with sqlalchemy
            flag_modified(survey_record, "survey")

        survey_record.survey["fields"][state]["data"] = user_input_msg
        survey_record.survey["fields"][state]["submission_time"] = user_submission_time

        survey_record.submission_time = user_submission_time
        return

    @classmethod
    def get_next_question(cls, survey_record):
        try:
            survey_record.state += 1
            return survey_record.survey["fields"][survey_record.state]["question"]
        except IndexError:
            survey_record.state = -1
            return cls.complete_msg

    @classmethod
    def get_survey_specs(cls):
        return yaml.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "earthquake.yaml")))

    @classmethod
    def init_survey(cls, survey_record):
        survey_record.survey = {"fields": cls.generic_survey_fields}
        return
