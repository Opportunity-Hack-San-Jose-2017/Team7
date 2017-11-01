import yaml
import os
import logging
import json
import requests

from platobot.config import FacebookConfig
from platobot.surveys.survey_manager import SurveyManager

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
            self.send_response(survey_record.user, response)

    def get_survey_specs(self):
        return yaml.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "facebook/violence.yaml")))

    def get_generic_survey_fields(self):
        return self.generic_survey_fields

    def send_response(self, recipient_id, response):
        """
        Have the bot reply to user
        """

        log.info("sending message to {recipient}: {text}".format(recipient=recipient_id, text=response["text"]))

        params = {
            "access_token": FacebookConfig.PAGE_ACCESS_TOKEN
        }
        headers = {
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "recipient": {
                "id": recipient_id
            },
            "message": response
        })
        r = requests.post(FacebookConfig.FACEBOOK_MESSAGEING_API, params=params, headers=headers, data=data)
        if r.status_code != 200:
            log.info(r.status_code)
            log.info(r.text)
