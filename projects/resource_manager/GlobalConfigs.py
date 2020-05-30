import json

from resource_manager.Singleton import Singleton


class GlobalConfigs(metaclass=Singleton):
    @staticmethod
    def instance():
        return GlobalConfigs()

    def __init__(self):
        self.config = None
        self.config_name = "config.json"
        self.node_ip = 'localhost'
        self.port = 3000

    def get_port(self):
        return self.port

    def set_port(self, port):
        self.port = port

    def set_config(self, name):
        self.config_name = name
        config_path = "./config/" + name
        if self.config is None:
            with open(config_path, 'r') as f:
                self.config = json.load(f)

    def assert_config(self):
        if self.config is None:
            raise Exception("You must set config first!")

    def set_node_ip(self, ip):
        self.node_ip = ip

    def get_node_ip(self):
        return self.node_ip

    def get_config(self, name):
        self.assert_config()
        if name is None:
            return self.config
        else:
            return self.config.get(name)

    def lookup_rule(self, data):
        self.assert_config()
        rules = self.config.get('rules')

        rules = list(filter(lambda x: x['name'] == data['name'], rules))
        if len(rules) == 1:
            return {
                **rules[0],
                **data
            }
        else:
            raise Exception("Rule with name " + data['name'] + " not found!")
