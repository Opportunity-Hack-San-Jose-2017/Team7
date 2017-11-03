import yaml
import os
import logging
from platobot.surveys.survey_manager import SurveyManager
from platobot.utils.facebook_api import send_response
from platobot.ushahidi import ushahidi_http, ds

log = logging.getLogger(__name__)

class FacebookSurveyManager(SurveyManager):
    def __init__(self):

        self.generic_survey_fields = yaml.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                 "facebook/kenya.yaml")))
        self.complete_msg = {"text": "Report completed!"}
        self.ushahidi_client = ushahidi_http.UshahidiClient()
        forms = self.ushahidi_client.get_forms()
        self.form = None
        self.form_attributes = None
        for form in forms:
            if 'kenya' in form.name.lower():
                self.form = form
                break
        self.form_attributes = self.ushahidi_client.get_attributes(self.form.id)
        for attribute in self.form_attributes:
            log.info(str(attribute))
            log.info(str(attribute.instructions))
            log.info(str(attribute.key))

    def send_response_to_user(self, survey_record):
        try:
            survey_record.state += 1
            response = survey_record.survey["fields"][survey_record.state]
        except IndexError:
            survey_record.state = -1
            response = self.complete_msg
            self._survey_complete_hook(survey_record.user)
        finally:
            send_response(survey_record.user, response)

    def _survey_complete_hook(self, user):
        """
        This hook is called after survery is completed
        :return:
        """
        # session = db_interface.new_session()
        # record = session.query(models.Survey).filter(
        #     models.Survey.user == user,
        #     models.Survey.state != -1
        #     ).order_by(sqlalchemy.desc(models.Survey.message_submission_time)).first()
        # session.close()
        # print(record)

        # notes, the "key" need to be used in values
        # Location
        # key: 448ed837-eecb-4306-967e-b394540ea863
        # How urgent is the situation?
        # key: 4f48b8c4-7615-405d-9113-1844371ba01e
        post = ds.Post(title='Violent cats - sms edition', content='We are just testing this survey',
                       values={
                           '448ed837-eecb-4306-967e-b394540ea863': [{"lat": "-11.7014801", "lon": "27.4809511429148"}],
                           '4f48b8c4-7615-405d-9113-1844371ba01e': ["Not Urgent"]
                        },
                       status='published')
        post.set_form(self.form)
        self.ushahidi_client.save_post(post)
        log.info('Sent to Ushahidi')

    def get_survey_specs(self):
        """this won't be used anymore since we are getting survey from Ushahidi"""
        return yaml.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "facebook/violence.yaml")))

    def get_generic_survey_fields(self):
        return self.generic_survey_fields
