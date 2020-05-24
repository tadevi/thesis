import json

from modules.utils import config_name
from rule_engine.HandleScalar import HandleScalar
from rule_engine.HandleStream import HandleStream
from rule_engine.UrlToStream import UrlToStream


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
