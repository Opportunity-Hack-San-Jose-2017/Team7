import yaml
import os
import logging
from sqlalchemy.orm.attributes import flag_modified
from twilio.rest import Client

from platobot.surveys.survey_manager import SurveyManager
from platobot.config import TwilioConfig
from platobot.ushahidi import ushahidi_http, ds
from pygeocoder import Geocoder

log = logging.getLogger(__name__)

class SMSSurveyManager(SurveyManager):

    def __init__(self):
        #self.generic_survey_fields = yaml.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        #                                                         "sms/generic.yaml")))
        self.complete_msg = 'Report completed.'
        self.ushahidi_client = ushahidi_http.UshahidiClient()
        self.init_generic_survey()

    def send_response_to_user(self, survey_record):
        try:
            self._survey_complete_hook(survey_record)
            survey_record.state += 1
            response = survey_record.survey["fields"][survey_record.state]["text"]
        except IndexError:
            survey_record.state = -1
            response = self.complete_msg
        finally:
            self.send_response(survey_record.user, response)

    def _survey_complete_hook(self, survey_record):
        """
        This hook is called after survey is completed
        :return:
        """

        title = ''
        description = ''
        values = {}
        fields = survey_record.survey["fields"]
        for field in fields:
            if field.get('key') == 'title':
                if field.get('data'):
                    title = field.get('data')
            elif field.get('key') == 'description':
                if field.get('data'):
                    description += '\n' + field.get('data')

            # here should check for other values using the attribute key
            elif field.get('input') == 'location':
                # if it doesn't have lat, long, we're in trouble??
                loc = field.get('data') # "latitude: 37.4213457, longitude: -121.8619215"
                # ;)
                log.info("user: {}".format(loc))
                if loc:
                    lat, lon = None, None
                    coord = loc.split(',')
                    if len(coord) == 2:
                        try:
                            coord[0].strip()
                            coord[1].strip()
                            lat, lon = float(coord[0]), float(coord[1])
                        except:
                            pass

                    if lat is None and lon is None:
                        try:
                            result = Geocoder.geocode(loc)
                            if result.valid_address:
                                lat, lon = result.coordinates
                                log.info("valid: {}, {}".format(lat, lon))
                        except:
                            pass

                    if lat is None and lon is None:
                        description += "Location: {}".format(loc)
                        # log.info("user: {}, {}".format(lat, lon))

                    # values['448ed837-eecb-4306-967e-b394540ea863'] = [{"lat": lat, "lon": lon}]
                    if field.get('key') is not None and lat is not None and lon is not None:
                        values[field.get('key')] = [{"lat": lat, "lon": lon}]

            else:
                if field.get('data'):
                    if field.get('key') is not None:
                        values[field.get('key')] = [field.get('data')]

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
        if title:
            if survey_record.post_id is None:
                post = ds.Post(title=title, content=description, values=values, status='published')
                forms = self.ushahidi_client.get_forms()
                log.info("got forms")
                for form in forms:
                    log.info("form name = " + form.name)
                    log.info("survey_record.form_name = " + survey_record.form_name)
                    if survey_record.form_name == form.name:
                        log.info("got the form")
                        post.set_form(form)
                        break
                post = self.ushahidi_client.save_post(post)
                survey_record.post_id = post.id
                print("post id = {}".format(survey_record.post_id))
                log.info('Created new post on Ushahidi')
            else:
                post = self.ushahidi_client.get_post(survey_record.post_id)
                if description:
                    post.content = description
                post.values = values
                self.ushahidi_client.update_post(post)
                log.info('Updated post on Ushahidi')

    def get_survey_specs(self, survey_record):
        """this won't be used anymore since we are getting survey from Ushahidi"""
        #return yaml.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "sms/earthquake.yaml")))
        forms = self.ushahidi_client.get_forms()
        log.info("survey_record.unprocessed_user_message = " + survey_record.unprocessed_user_message)
        log.info(forms)
        for form in forms:
            log.info("form name = " + form.name)
            if survey_record.unprocessed_user_message.rstrip('.').lower() in form.name.lower():
                log.info("found form")
                survey_record.form_name = form.name
                self.form = form
                break
        self.form_attributes = self.ushahidi_client.get_attributes(self.form.id)

        self.survey_fields = []

        # build the form here and remember to store the keys for attributes
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
            log.info(str(attribute.misc_json_data))
            # options = ["Life threatening", "It can wait a few hours", "Not urgent"]
            if attribute.type_ == 'title' or attribute.type_ == 'description':
                self.survey_fields.append({'text': attribute.instructions, "key": attribute.type_,
                                                   "priority": attribute.misc_json_data.get('priority')})
            else:
                # note: location has a specific input==location
                item = {
                    "text": attribute.instructions,
                    "key": attribute.key,
                    "input": attribute.input,
                    "type": attribute.type_,
                    "priority": attribute.misc_json_data.get('priority')
                }

                if attribute.misc_json_data.get('options') is not None and len(
                        attribute.misc_json_data.get('options')) > 0:
                    options = attribute.misc_json_data.get('options')
                    option_txt = '. '.join(options)
                    item['text'] += ' Options: ' + option_txt + '.'

                self.survey_fields.append(item)
        self.survey_fields.sort(key=lambda x: x['priority'])

        return self.survey_fields

    def get_generic_survey_fields(self):
        return self.generic_survey_fields

    def init_generic_survey(self):
        self.generic_survey_fields = [{'text': 'first message'}]
        forms = self.ushahidi_client.get_forms()

        options = []
        for form in forms:
            options.append(form.name.split('Report')[0].strip())

        self.generic_survey_fields.append({'text': 'What do you want to report on? Options: ' + '. '.join(options) + '.'})
        log.info("updated ")

    def send_response(self, user_number, response):
        """
        Have the bot reply to user
        """
        client = Client(TwilioConfig.ACCOUNT_SID, TwilioConfig.AUTH_TOKEN)

        client.api.account.messages.create(
            to=user_number,
            from_=TwilioConfig.NUMBER,
            body=response)
