import json
from importlib import import_module

config_name = 'config/config.json'


# parse_stream---> emit
# process_stream : input -> output
# send_stream -> input... ->stream

class RuleEngine:
    def __init__(self):
        self.modules = {}

    def getModule(self, name, package):
        packageKey = package + '.' + name
        if self.modules.get(packageKey) is None:
            module = import_module('.' + name, package)
            self.modules[packageKey] = module
        return self.modules[packageKey]

    def run(self, input):
        with open(config_name, 'r') as f:
            json_config = json.load(f)

            for rule in json_config['rules']:
                if rule['data_type'] == 'scalar':
                    value = input
                    for module_define in rule['modules']:
                        module = self.getModule(module_define['name'], module_define['package'])
                        config = module_define.get('configs')

                        main = getattr(module, 'Main')
                        if value is None:
                            value = ''
                        value = main(config).run(value)
                    return value
                elif rule['data_type'] == 'stream':
                    # handle stream type
                    print('stream')
