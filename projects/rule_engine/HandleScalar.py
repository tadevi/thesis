from importlib import import_module

from modules.base import Filter, Map
from resource_manager.ThreadTask import ThreadTask


def __getModule__(module):
    configs = {}
    if not module.get('configs') is None:
        configs = module['configs']
    call = import_module('.' + module['name'], module['package'])
    main = getattr(call, 'Main')
    return {
        'configs': configs,
        'call': call,
        'main': main(configs)
    }


class HandleScalar(ThreadTask):
    def __init__(self, configs, input):
        super().__init__()
        self.configs = configs
        self.input = input
        self.modules = list(map(__getModule__, configs['modules']))

    def run(self):
        for module in self.modules:
            if isinstance(module['main'], Filter):
                if not module['main'].run(self.input):
                    return None
            elif isinstance(module['main'], Map):
                self.input = module['main'].run(self.input)
            else:
                module['main'].run(self.input)
        return self.input
