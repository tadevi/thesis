import json
from importlib import import_module

config_name = 'config/config.json'

# parse_stream---> emit
# process_stream : input -> output
# send_stream -> input... ->stream

def run(input):
    with open(config_name, 'r') as f:
        json_config = json.load(f)

        for rule in json_config['rules']:
            if rule['data_type'] == 'scalar':
                value = input
                for module in rule['modules']:
                    module_call = import_module('.' + module['name'], module['package'])
                    module_config = module.get('configs')

                    main = getattr(module_call, 'Main')
                    if value is None:
                        value = ''
                    value = main(module_config).run(value)
                return value
            elif rule['data_type'] == 'stream':
                # handle stream type
                print('stream')


run('abc')
