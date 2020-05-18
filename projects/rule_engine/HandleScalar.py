from importlib import import_module

from modules.base import Filter, Map


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


class HandleScalar:
    def __init__(self, configs):
        self.modules = list(map(__getModule__, configs['modules']))

    def run(self, inputs):
        value = inputs
        for module in self.modules:
            if isinstance(module['main'], Filter):
                if not module['main'].run(value):
                    return None
            elif isinstance(module['main'], Map):
                value = module['main'].run(value)
            else:
                module['main'].run(value)
        return value
