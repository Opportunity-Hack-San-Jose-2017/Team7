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

        # TODO: build the form here and remember to store the keys for attributes
        # example:
        # Location
        # key: 448ed837-eecb-4306-967e-b394540ea863
        # How urgent is the situation?
        # key: 4f48b8c4-7615-405d-9113-1844371ba01e
        # later use keys to look up and store as values

        for attribute in self.form_attributes:
            log.info(str(attribute))
            log.info(str(attribute.instructions))
            log.info(str(attribute.key))
            # title type is title always
            # description type is description always
            log.info(str(attribute.type_))
            if attribute.type_ == 'title':
                self.title_instruction = attribute.instructions
            elif attribute.type_ == 'description':
                self.description_instruction = attribute.instructions
            elif attribute.input == 'location': # only specific to location
                self.location_instruction = attribute.instructions


    def send_response_to_user(self, survey_record):
        try:
            survey_record.state += 1
            response = survey_record.survey["fields"][survey_record.state]
        except IndexError:
            survey_record.state = -1
            response = self.complete_msg
            self._survey_complete_hook(survey_record)
        finally:
            send_response(survey_record.user, response)

    def _survey_complete_hook(self, survey_record):
        """
        This hook is called after survery is completed
        :return:
        """
        print('survey_record')
        print(survey_record.survey["fields"])
        print(survey_record.survey["fields"][0]["data"])

        title = ''
        description = ''
        values = {}
        fields = survey_record.survey["fields"]
        for field in fields:
            if field.get('text') == self.title_instruction:
                title = field.get('data')
            elif field.get('text') == self.description_instruction:
                description = field.get('data')

            # here should check for other values using the attribute key
            elif field.get('text') == 'What is your location?':
                loc = field.get('data') # "latitude: 37.4213457, longitude: -121.8619215"
                # ;)
                lat = float(loc.split(',')[0].split(':')[1])
                lon = float(loc.split(',')[1].split(':')[1])
                values['448ed837-eecb-4306-967e-b394540ea863'] = [{"lat": lat, "lon": lon}]
            elif field.get('text') == 'How urgent is the situation?':
                values['4f48b8c4-7615-405d-9113-1844371ba01e'] = [field.get('data')]

        # notes, the "key" need to be used in values, should grab keys dynamically ^^^
        # Location
        # key: 448ed837-eecb-4306-967e-b394540ea863
        # How urgent is the situation?
        # key: 4f48b8c4-7615-405d-9113-1844371ba01e
        # post = ds.Post(title=title, content=description,
        #                values={
        #                    '448ed837-eecb-4306-967e-b394540ea863': [{"lat": "-11.7014801", "lon": "27.4809511429148"}],
        #                    '4f48b8c4-7615-405d-9113-1844371ba01e': ["Not Urgent"]
        #                 },
        #                status='published')

        post = ds.Post(title=title, content=description, values=values, status='published')
        post.set_form(self.form)
        self.ushahidi_client.save_post(post)
        log.info('Sent to Ushahidi')

    def get_survey_specs(self):
        """this won't be used anymore since we are getting survey from Ushahidi"""
        return yaml.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "facebook/violence.yaml")))

    def get_generic_survey_fields(self):
        return self.generic_survey_fields
