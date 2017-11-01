import multiprocessing

# Item pushed on the work queue to tell the worker threads to terminate
SENTINEL = "QUIT"


def is_sentinel(obj):
    """Predicate to determine whether an item from the queue is the
    signal to stop"""
    return type(obj) is str and obj == SENTINEL


class PoolWorker(multiprocessing.Process):
    """Process that consumes WorkUnits from a queue to process them"""

    def __init__(self, queue, *args, **kwds):
        """\param workq: Queue object to consume the work units from"""
        multiprocessing.Process.__init__(self, *args, **kwds)
        self.queue = queue

    def run(self):
        """Process the work unit, or wait for sentinel to exit"""
        while 1:
            work_unit = self.queue.get()
            # Run the job / sequence
            work_unit.process()


class Pool(object):
    """
    The Pool class represents a pool of worker threads. It has methods
    which allows tasks to be offloaded to the worker processes in a
    few different ways
   """

    def __init__(self, num_workers, name="Pool"):
        """
        \param num_workers (integer) number of worker threads to start
        \param name (string) prefix for the worker threads' name
        """
        self.queue = multiprocessing.Manager().Queue()
        self.workers = []

        for idx in range(num_workers):
            process = PoolWorker(self.queue, name="%s-Worker-%d" % (name, idx))
            process.daemon = True
            try:
                process.start()
            except:
                # If one thread has a problem, undo everything
                self.terminate()
                raise
            else:
                self.workers.append(process)

    def submit(self, work_unit):
        self.queue.put(work_unit)

    def terminate(self):
        """Stops the worker processes immediately without completing
        outstanding work. When the pool object is garbage collected
        terminate() will be called immediately."""

        # Clearing the job queue
        try:
            while 1:
                self.queue.get_nowait()
        # except Manager().Queue.empty():
        except:
            pass

        # Send one sentinel for each worker thread: each thread will die
        # eventually, leaving the next sentinel for the next thread
        for process in self.workers:
            self.queue.put(SENTINEL)
