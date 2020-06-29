import json

from resource_manager.Singleton import Singleton
from modules.network import Network
from modules.utils import log, get_ip


class GlobalConfigs(metaclass=Singleton):
    @staticmethod
    def instance():
        return GlobalConfigs()

    def __init__(self):
        self.tag = "GlobalConfigs"
        self.config = None
        self.ip = 'localhost'
        self.port = 3000
        self.node_meta_name = "node_meta.json"

    def init_configs(self):
        with open(self.node_meta_name, 'r') as f:
            meta = json.load(f)
            id = meta.get("id")
            self.layer, self.position = id.split('.')
            self.layer = int(self.layer)
            self.position = int(self.position)
            self.name = meta.get("name")
            self.storage = meta.get("storage")
            self.port = meta.get("port")
            self.cloud_url = meta.get("cloud_url")
            self.is_cloud = meta.get("is_cloud")

        if self.is_cloud:
            with open("nodes_ip.json", 'r') as f:
                self.nodes_ip = json.load(f)

            with open("config/cloud.json", 'r') as f:
                self.config = json.load(f)
        else:
            network = Network({})

            res = network.get(self.cloud_url + "/config", {
                "layer": self.layer,
                "position": self.position
            })
            self.config = res.get("data")

            log.v(self.tag, "Obtained config from cloud:\n", self.config)

        self.ip = get_ip()

        log.v(self.tag, "Resolved IP Address:", self.ip)

    def get_port(self):
        return self.port

    def get_node_ip(self):
        return self.ip

    def assert_config(self):
        if self.config is None:
            raise Exception("You must set config first!")

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

    def get_fog1_config(self, fog2_ip, fog2_port, cloud_ip, cloud_port):
        with open("config/fog1.json", 'r') as f:
            config = json.load(f)
            config.get("rules")[1].get("modules")[1].get("configs")["cloud_url"] = self.get_base_url(cloud_ip,
                                                                                                     cloud_port)
            config.get("rules")[1].get("modules")[2].get("configs")["cloud_url"] = self.get_base_url(fog2_ip, fog2_port)
            config.get("rules")[2].get("modules")[1].get("configs")["cloud_url"] = self.get_base_url(cloud_ip,
                                                                                                     cloud_port)
            return config

    def get_fog2_config(self, cloud_ip, cloud_port):
        with open("config/fog2.json", 'r') as f:
            config = json.load(f)
            config.get("rules")[0].get("modules")[0].get("configs")["cloud_url"] = self.get_base_url(cloud_ip,
                                                                                                     cloud_port)
            config.get("rules")[0].get("modules")[1].get("configs")["cloud_url"] = self.get_base_url(cloud_ip,
                                                                                                     cloud_port)
            return config

    def get_base_url(self, ip, port):
        return "http://" + ip + ":" + port
