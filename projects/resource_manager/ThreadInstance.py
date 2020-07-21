import traceback
from queue import Queue

from modules import log
from resource_manager.ThreadTask import ThreadTask, ThreadTaskTerminate


class ThreadInstance:
    def __init__(self):
        self.queue = Queue()
        self._available = True

    def put_job(self, job):
        if isinstance(job, ThreadTask):
            self.queue.put(job)
        else:
            raise Exception("Only allow ThreadTask object")

    def is_thread_available(self):
        return self._available

    def kill(self):
        self.queue.put(ThreadTaskTerminate())

    def run(self):
        while True:
            try:
                self._available = False
                job = self.queue.get()
                if isinstance(job, ThreadTaskTerminate):
                    break
                log.i("ThreadInstance " + str(id(self)), "Starting a job " + str(id(job)))
                job.run()
                log.i("ThreadInstance " + str(id(self)), "Finish a job " + str(id(job)))
                # if self.queue.empty():
                #     self._available = True
            except:
                log.e("ThreadInstance " + str(id(self)), traceback.format_exc())
            self._available = self.queue.empty()
