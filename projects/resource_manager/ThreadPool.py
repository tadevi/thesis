from threading import Thread

from modules import log
from resource_manager.Singleton import Singleton
from resource_manager.ThreadInstance import ThreadInstance


class ThreadPool(metaclass=Singleton):
    @staticmethod
    def instance():
        return ThreadPool()

    def __init__(self):
        self.threads = []
        self.thread_count = 0
        self.min_thread = 0
        for i in range(0, self.min_thread):
            self.create_thread()

    def find_first(self):
        for i in self.threads:
            if i.is_thread_available():
                return i
        return None

    def create_thread(self):
        thread_instance = ThreadInstance()
        self.threads.append(thread_instance)
        new_thread = Thread(target=thread_instance.run, daemon=True)
        new_thread.start()
        log.v("ThreadPool", "Spawn a new thread!!!!")
        self.thread_count += 1
        return thread_instance

    def get_thread(self):
        thread_instance = self.find_first()
        if thread_instance is None:
            thread_instance = self.create_thread()

        return thread_instance

    def clean(self):
        for i in self.threads:
            i.kill()
