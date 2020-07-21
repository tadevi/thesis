import time
from importlib import import_module
from queue import Queue

from modules import log, utils
from modules.base import Filter, Map
from modules.stream import mjpeg
from resource_manager.GlobalConfigs import GlobalConfigs
from resource_manager.ThreadPool import ThreadPool
from resource_manager.ThreadTask import ThreadTask
from rule_engine.UrlToStream import UrlToStream

tag = "HandleStream"


def __getModule__(cam, module):
    configs = cam

    if not module.get('configs') is None:
        configs = {
            **configs,
            **module['configs']
        }

    call = import_module('.' + module['name'], module['package'])
    main = getattr(call, 'Main')

    return {
        'configs': configs,
        'call': call,
        'main': main(configs)
    }


class HandleStream(ThreadTask):
    def __init__(self, configs, input):
        super().__init__()
        self.configs = configs
        self.input = input
        self.modules = list(map(lambda x: __getModule__(self.input, x), configs))

        self.url_to_stream = UrlToStream(self.input)
        self.queue = Queue(maxsize=3)
        task = ThreadTask(run=self.start_reading_frames)
        ThreadPool.instance().get_thread().put_job(task)

    def start_reading_frames(self):
        log.v(tag, "start_reading_frames")
        while True:
            frame = self.url_to_stream.get()
            if self.queue.full():
                self.queue.get()
            self.queue.put(frame)
            # time.sleep(GlobalConfigs.instance().FPS)

    def run(self):
        while True:
            # frame = self.url_to_stream.get()
            # time.sleep(GlobalConfigs.instance().FPS)
            if self.queue.empty():
                continue
            frame = self.queue.get()
            if frame is None:
                continue
                # print("clear from channel")
                # clear_from_channel(self.configs['camera_id'])
                # break
            _continue = False
            for module in self.modules:
                if isinstance(module['main'], Filter):
                    if not module['main'].run(frame):
                        _continue = True
                        break
                elif isinstance(module['main'], Map):
                    frame = module['main'].run(frame)
                else:
                    module['main'].run(frame)
