import yaml
import os
import logging
from platobot.surveys.survey_manager import SurveyManager
from platobot.utils.facebook_api import send_response
from platobot.ushahidi import ushahidi_http, ds

log = logging.getLogger(__name__)

class FacebookSurveyManager(SurveyManager):
    def __init__(self):

        #self.generic_survey_fields = yaml.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        #                                                         "facebook/kenya.yaml")))
        #print(self.generic_survey_fields)
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

        # build the form here and remember to store the keys for attributes
        # example:
        # Location
        # key: 448ed837-eecb-4306-967e-b394540ea863
        # How urgent is the situation?
        # key: 4f48b8c4-7615-405d-9113-1844371ba01e
        # later use keys to look up and store as values

        self.generic_survey_fields = [{'text': 'first msg', 'priority': 0}]
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
                self.generic_survey_fields.append({'text': attribute.instructions, "key": attribute.type_, "priority": attribute.misc_json_data.get('priority') })
            else:
                # note: location has a specific input==location
                item = {
                    "text": attribute.instructions, 
                    "key": attribute.key,
                    "input": attribute.input,
                    "type": attribute.type_,
                    "priority": attribute.misc_json_data.get('priority')
                }
                if attribute.input == "location":
                    quick_replies = [{
                        "content_type": "location",
                        "title": "location",
                        "payload": "location"
                    }]
                    item['quick_replies'] = quick_replies

                if attribute.misc_json_data.get('options') is not None and len(attribute.misc_json_data.get('options')) > 0:
                    options = attribute.misc_json_data.get('options')
                    quick_replies = []
                    for op in options:
                        quick_replies.append({
                            "content_type": "text",
                            "title": op,
                            "payload": "payload"
                        })
                    item['quick_replies'] = quick_replies

                self.generic_survey_fields.append(item)
                print(self.generic_survey_fields)
        self.generic_survey_fields.sort(key=lambda x: x['priority'])
        print(self.generic_survey_fields)

    def send_response_to_user(self, survey_record):
        try:
            self._survey_complete_hook(survey_record)
            survey_record.state += 1
            response = survey_record.survey["fields"][survey_record.state]
        except IndexError:
            survey_record.state = -1
            response = self.complete_msg
        finally:
            send_response(survey_record.user, response)

    def _survey_complete_hook(self, survey_record):
        """
        This hook is called after survey is completed
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
            if field.get('key') == 'title':
                if field.get('data'):
                    title = field.get('data')
            elif field.get('key') == 'description':
                if field.get('data'):
                    description = field.get('data')

            # here should check for other values using the attribute key
            elif field.get('input') == 'location':
                # if it doesn't have lat, long, we're in trouble??
                loc = field.get('data') # "latitude: 37.4213457, longitude: -121.8619215"
                # ;)
                if loc:
                    coords = loc.split(',')
                    lat, lon = float(coords[0].split(':')[1].strip()), float(coords[1].split(':')[1].strip())
                    lat, lon = float("{0:.3f}".format(lat)), float("{0:.3f}".format(lon))

                    print("lat: {}, lon: {}".format(lat, lon))
                    # values['448ed837-eecb-4306-967e-b394540ea863'] = [{"lat": lat, "lon": lon}]
                    if field.get('key') is not None:
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
                post.set_form(self.form)
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

    def get_survey_specs(self):
        """this won't be used anymore since we are getting survey from Ushahidi"""
        return yaml.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "facebook/violence.yaml")))

    def get_generic_survey_fields(self):
        return self.generic_survey_fields
