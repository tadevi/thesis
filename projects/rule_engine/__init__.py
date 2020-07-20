import traceback

from modules import log
from resource_manager.Singleton import Singleton
from resource_manager.ThreadPool import ThreadPool
from rule_engine.HandleScalar import HandleScalar
from rule_engine.HandleStream import HandleStream
from rule_engine.UrlToStream import UrlToStream


class RuleEngine(metaclass=Singleton):
    @staticmethod
    def instance():
        return RuleEngine()

    def run(self, rules, input):
        for rule in rules:
            try:
                if rule['data_type'] == 'scalar':
                    ThreadPool.instance().get_thread().put_job(HandleScalar(rule['modules'], input))
                elif rule['data_type'] == 'stream':
                    ThreadPool.instance().get_thread().put_job(HandleStream(rule['modules'], input))
            except:
                log.e('RuleEngine', traceback.format_exc())
