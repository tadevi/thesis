import json
import traceback
from importlib import import_module
import os

config_name = 'config/config.json'


# parse_stream---> emit
# process_stream : input -> output
# send_stream -> input... ->stream

def handle_scalar(inputs, modules):
    value = inputs
    for module in modules:
        module_call = import_module('.' + module['name'], module['package'])
        module_config = module.get('configs')

        main = getattr(module_call, 'Main')
        if value is None:
            value = ''
        value = main(module_config).run(value)
    return value


def handle_stream(inputs, modules):
    print("Handle stream")


def run(inputs):
    with open(config_name, 'r') as f:
        json_config = json.load(f)
        for rule in json_config['rules']:
            if os.fork() == 0:
                try:
                    if rule['data_type'] == 'scalar':
                        handle_scalar(inputs, rule['modules'])
                    elif rule['data_type'] == 'stream':
                        handle_stream(inputs, rule['modules'])
                except:
                    pass  # traceback.print_exc()
