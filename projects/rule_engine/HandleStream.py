from importlib import import_module

from modules.base import Filter, Map
from rule_engine.MjpegToStream import MjpegToStream
from rule_engine.UrlToStream import UrlToStream
from server.channel import clear_from_channel


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


class HandleStream:
    def __init__(self, configs):
        self.configs = configs
        cam = {
            'camera_id': configs['camera_id'],
            'name': configs['name']
        }
        self.modules = list(map(lambda x: __getModule__(cam, x), configs['modules']))

        self.url_to_stream = UrlToStream(configs)

    def run(self):
        while True:
            frame = self.url_to_stream.get()
            if frame is None:
                clear_from_channel(self.configs['camera_id'])
                break
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
