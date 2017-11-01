import threading
import logging
import multiprocessing

from platobot.workers.pool import Pool
from platobot.workers.work_unit import WorkUnit
from platobot import models, constants

log = logging.getLogger(__name__)
db_interface = models.platobot_db


class Manager(threading.Thread):
    def __init__(self, num_workers, worker_name):
        threading.Thread.__init__(self, name=worker_name)

        self.pool = Pool(num_workers=num_workers, name=worker_name)

        self.in_progress_jobs = multiprocessing.Manager().list()
        self.lock = multiprocessing.Manager().Lock()

    def run(self):
        while 1:
            try:
                self.dispatch()
            except Exception:
                import traceback
                log.exception(traceback.format_exc())

    def dispatch(self):
        session = db_interface.new_session()
        records = session.query(models.Survey).filter(models.Survey.unprocessed_user_message != None,
                                                      models.Survey.state != -1).all()
        for record in records:
            self.submit_job(WorkUnit(record.id))
        session.close()

    def submit_job(self, work_unit):
        with self.lock:
            if work_unit.get_unique_key() in self.in_progress_jobs:
                return False

            self.in_progress_jobs.append(work_unit.get_unique_key())

        # Remember these shared memory references
        work_unit.in_progress_jobs = self.in_progress_jobs
        work_unit.lock = self.lock

        self.pool.submit(work_unit)

        return True