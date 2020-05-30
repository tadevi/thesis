import json
import traceback

from modules.utils import log
from resource_manager.GlobalConfigs import GlobalConfigs
from rule_engine.HandleScalar import HandleScalar
from rule_engine.HandleStream import HandleStream
from rule_engine.UrlToStream import UrlToStream


class RuleEngine:
    def __init__(self):
        pass

    def run(self, inputs):
        rules = GlobalConfigs.instance().get_config('rules')
        for rule in rules:
            try:
                if rule['data_type'] == 'scalar':
                    HandleScalar(rule['modules']).run(inputs)
                elif rule['data_type'] == 'stream':
                    HandleStream(rule['modules']).run()
            except:
                log.e('RuleEngine', traceback.format_exc())
