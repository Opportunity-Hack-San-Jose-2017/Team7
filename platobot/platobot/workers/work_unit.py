import logging

from platobot.surveys import get_survey_manager
from platobot import models

log = logging.getLogger(__name__)
db_interface = models.platobot_db


class WorkUnit(object):
    """
    A WorkUnit instance defines the Work which will be processed by a worker as defined
    in the process_pool class.  The Job Manager handles the dispatching of the WorkUnit.
    It allows only one unique instance of the WorkUnit as defined by get_unique_key()
    to be executed.
    """
    def __init__(self, survey_id):
        self.in_progress_jobs = None
        self.lock = None

        self.survey_id = survey_id

    def process(self):
        try:
            session = db_interface.new_session()
            record = session.query(models.Survey).filter(models.Survey.id == self.survey_id).first()

            if record:
                survey_manager = get_survey_manager(record.channel)

                survey_manager.record_user_response(record)
                survey_manager.send_response_to_user(record)

            session.commit()
            session.close()

        except Exception as e:
            log.exception("WorkUnit.process() hit exception {}".format(e))
        finally:
            if self.in_progress_jobs is not None and self.lock is not None:
                with self.lock:
                    if self.get_unique_key() in self.in_progress_jobs:
                        self.in_progress_jobs.remove(self.get_unique_key())

    def get_unique_key(self):
        """
        Returns an unique value which represents this instance.  An example is an
        unique prefix with the job id from a specific DB table (e.g. email_job_1).
        """
        return self.survey_id
