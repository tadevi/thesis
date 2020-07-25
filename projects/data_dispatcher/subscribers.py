from importlib import import_module
from queue import Queue, Full

from modules.base import Filter, Map
from resource_manager.ThreadPool import ThreadPool
from resource_manager.ThreadTask import ThreadTask


class Subscriber:
    def __init__(self, id, data, modules_meta):
        self.id = id
        self.__queue__ = Queue(maxsize=3)
        self.__is_canceled__ = False

        # start a separate thread for reading input
        task = ThreadTask(run=self.__start_consuming__, params=(data, modules_meta))
        ThreadPool.instance().get_thread().put_job(task)

    def on_next(self, item):
        try:
            self.__queue__.put(item, block=False)
        except Full:
            pass

    def on_unsubscribe(self):
        self.__is_canceled__ = True

    def __start_consuming__(self, data, modules_meta):
        modules = self.__create_modules__(data, modules_meta)

        while not self.__is_canceled__:
            item = self.__queue__.get()
            if item is not None:
                for module in modules:
                    if isinstance(module['main'], Filter):
                        if not module['main'].run(item):
                            break
                    elif isinstance(module['main'], Map):
                        item = module['main'].run(item)
                    else:
                        module['main'].run(item)

    def __create_modules__(self, data, modules_meta):
        modules = []
        for module_meta in modules_meta:
            configs = {}
            if module_meta.get('configs') is not None:
                configs = {
                    **module_meta['configs'],
                    **data
                }

            call = import_module('.' + module_meta['name'], module_meta['package'])
            main = getattr(call, 'Main')

            module = {
                'configs': configs,
                'call': call,
                'main': main(configs)
            }
            modules.append(module)
        return modules
