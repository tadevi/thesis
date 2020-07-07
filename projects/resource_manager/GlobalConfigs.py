import json
import os
import shutil
import zipfile

from resource_manager.Singleton import Singleton
from modules.network import Network
from modules.utils import log, get_ip

tag = "GlobalConfigs"


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
        self.project_root = None

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
            self.last_update_time = meta.get("last_update_time")

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

            res = network.get(self.cloud_url + "/last_update")
            last_update_time = res.get("data").get("last_update_time")
            if last_update_time != self.last_update_time:
                modules_zip_path = os.path.join(self.project_root, "modules_download.zip")
                res = network.download_file(save_path=modules_zip_path, url=self.cloud_url + "/update")

                # delete modules folder
                modules_path = os.path.join(self.project_root, "modules")
                shutil.rmtree(modules_path)
                log.v(tag, "Deleted", modules_path)

                # unzip
                with zipfile.ZipFile(modules_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.project_root)
                log.v(tag, "Extracted zip to", self.project_root)

                # update last_update_time
                last_update_time = int(res.headers["last_update_time"])
                self.last_update_time = last_update_time
                meta["last_update_time"] = last_update_time
                meta_path = os.path.join(self.project_root, self.node_meta_name)
                with open(meta_path, 'w') as f:
                    json.dump(meta, f, indent=4)
                log.v(tag, "Last update time:", last_update_time)
            else:
                log.v(tag, "No update needed")

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
