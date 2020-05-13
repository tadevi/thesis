from queue import Queue

from modules.base import Map
from protocols.http import add_to_channel


class Main(Map):
    def __init__(self, configs):
        self.configs = configs
        self.queue = Queue(maxsize=3)
        add_to_channel('0', self.queue)

    def run(self, inputs):
        super(Main, self).run(inputs)
        if self.queue.full():
            self.queue.get()
        self.queue.put(inputs)
