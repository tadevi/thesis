import json

from rule_engine.HandleScalar import HandleScalar
from rule_engine.HandleStream import HandleStream
from rule_engine.UrlToStream import UrlToStream

config_name = 'config/config.json'


def lookup_rule(input):
    with open(config_name, 'r') as f:
        json_config = json.load(f)
        rules = json_config['rules']
        rules = list(filter(lambda x: x['name'] == input['name'], rules))
        if not len(rules) == 1:
            return "Rule for this type not found!"
        return {
            **rules[0],
            **input
        }


class RuleEngine:
    def __init__(self):
        pass

    def run(self, inputs):
        with open(config_name, 'r') as f:
            json_config = json.load(f)
            for rule in json_config['rules']:
                try:
                    if rule['data_type'] == 'scalar':
                        HandleScalar(rule['modules']).run(inputs)
                    elif rule['data_type'] == 'stream':
                        HandleStream(rule['modules']).run()
                except:
                    pass  # traceback.print_exc()
