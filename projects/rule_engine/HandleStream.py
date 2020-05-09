from importlib import import_module

from modules.base import Filter, Map
from rule_engine.UrlToStream import UrlToStream


def __getModule__(module):
    configs = {}
    if not module.get('config') is None:
        configs = module['config']
    call = import_module('.' + module['name'], module['package'])
    main = getattr(call, 'Main')
    return {
        'configs': configs,
        'call': call,
        'main': main(configs)
    }


#
#   configs: {
#       url: 'rtsp;//192.168.100.14:5540/ch0'
#   }
#

class HandleStream:
    def __init__(self, configs):
        self.modules = list(map(__getModule__, configs['modules']))
        self.url_to_stream = UrlToStream(configs)

    def run(self):
        while True:
            frame = self.url_to_stream.get()
            _continue = False
            for module in self.modules:
                if isinstance(module['main'], Filter):
                    if not module['main'].run(frame):
                        _continue = True
                        break
                elif isinstance(module['main'], Map):
                    frame = module['main'].run(frame)
                else:
                    break
