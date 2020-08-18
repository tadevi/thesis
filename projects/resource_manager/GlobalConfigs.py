import json
import os
import shutil
import time
import zipfile
from pathlib import Path

from resource_manager.Singleton import Singleton
from modules.network import Network
from modules import utils, log

tag = "GlobalConfigs"


class GlobalConfigs(metaclass=Singleton):
    @staticmethod
    def instance():
        return GlobalConfigs()

    def __init__(self):
        self.tag = "GlobalConfigs"
        self.config = None
        self.internal_ip = 'localhost'
        self.external_ip = '0.0.0.0'
        self.port = 3000
        self.node_meta_name = "node_meta.json"
        self.project_root = None
        # for stream
        self.FPS = 1 / 24
        self.test_on_local = True

    def init_node(self):
        with open("common_meta.json", 'r') as f:
            common_meta = json.load(f)
            self.test_on_local = common_meta.get('test_on_local') == "true"
            self.cloud_url = common_meta.get("cloud_url")

        with open(self.node_meta_name, 'r') as f:
            node_meta = json.load(f)

        self.name = node_meta.get("name")
        self.storage = node_meta.get("storage")
        self.port = node_meta.get("port")
        self.is_cloud = node_meta.get("is_cloud")
        self.last_update_time = node_meta.get("last_update_time")

        self.internal_ip = utils.get_internal_ip()
        log.v(self.tag, "Resolved internal IP Address:", self.internal_ip)

        self.external_ip = utils.get_external_ip()
        log.v(self.tag, "Resolved external IP Address:", self.external_ip)

        if self.is_cloud:
            with open("nodes_ip.json", 'r') as f:
                self.nodes_ip = json.load(f)

            self.config = self.parse_config("cloud")
        else:
            # get layer & position from cloud
            res = Network.instance().get(self.cloud_url + "/node_id", {
                "ip": self.external_ip,
                "port": self.port
            })
            if res.get('status_code') == 200:
                id = res.get('data').get("id")
                log.v(tag, "Obtained id from cloud:", id)
            else:
                id = node_meta.get("id")
                log.v(tag, "Obtained id from local:", id)

            self.layer, self.position = id.split('.')
            self.layer = int(self.layer)
            self.position = int(self.position)

            self.check_for_update()

    def check_for_update(self):
        config_name = "fog" + str(self.layer)

        res = Network.instance().get(self.cloud_url + "/last_update")
        if res.get('status_code') != 200:
            log.v(self.tag, "Cannot connect to Cloud")
            last_update_time = self.last_update_time
        else:
            last_update_time = res.get("data").get("last_update_time")

        if last_update_time != self.last_update_time:
            res = Network.instance().get(self.cloud_url + "/config", {
                "layer": self.layer,
                "position": self.position,
                "ip": self.external_ip,
                "port": self.port
            })
            self.config = res.get("data")

            log.v(self.tag, "Obtained config from cloud")

            self.cache_configs(config_name, self.config)

            modules_zip_path = os.path.join(self.project_root, "modules_download.zip")
            res = Network.instance().download_file(save_path=modules_zip_path, url=self.cloud_url + "/update")

            # delete modules folder
            # modules_path = os.path.join(self.project_root, "modules")
            # shutil.rmtree(modules_path)
            # log.v(tag, "Deleted", modules_path)

            # unzip
            with zipfile.ZipFile(modules_zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.project_root)
            log.v(tag, "Extracted zip to", self.project_root)

            # update last_update_time
            self.last_update_time = int(res.headers["last_update_time"])

            with open(self.node_meta_name, 'r') as f:
                meta = json.load(f)
            meta["last_update_time"] = self.last_update_time
            meta_path = os.path.join(self.project_root, self.node_meta_name)
            with open(meta_path, 'w') as f:
                json.dump(meta, f, indent=4)
            log.v(tag, "Last update time:", self.last_update_time)
        else:
            log.v(tag, "No update needed, use local configs and modules")

            self.config = self.parse_config(config_name, folder_name="config_cache")

    def cache_configs(self, config_name, configs):
        config_cache_folder_relative_path = "config_cache" + "/" + config_name

        rules = configs['rules']
        configs = {x: configs[x] for x in configs if x != 'rules'}

        config_cache_folder = os.path.join(self.project_root, config_cache_folder_relative_path)
        Path(config_cache_folder).mkdir(parents=True, exist_ok=True)
        with open(config_cache_folder_relative_path + "/" + config_name + ".json", 'w') as f:
            json.dump(configs, f, indent=4)

        rules_name = list(rules.keys())
        for rule_name in rules_name:
            Path(config_cache_folder + "/" + rule_name).mkdir(parents=True, exist_ok=True)
            rule_files_name = ["rule" + str(i) + ".json" for i in range(1, len(rules[rule_name]) + 1)]
            for idx, rule_file_name in enumerate(rule_files_name):
                with open(config_cache_folder_relative_path + "/" + rule_name + "/" + rule_file_name, 'w') as f:
                    json.dump(rules[rule_name][idx], f, indent=4)
        log.v(tag, "Cached configs")

    def get_port(self):
        return self.port

    def get_node_ip(self):
        return self.internal_ip if self.test_on_local else self.external_ip

    def assert_config(self):
        if self.config is None:
            raise Exception("You must set config first!")

    def get_config(self, name):
        self.assert_config()
        if name is None:
            return self.config
        else:
            return self.config.get(name)

    def lookup_rules(self, rule_name):
        self.assert_config()
        rules = self.config.get('rules').get(rule_name)

        if len(rules) > 0:
            return rules
        else:
            raise Exception("Rule with name " + rule_name + " not found!")

    def get_fog1_config(self, cloud_ip, cloud_port, fog2_ip, fog2_port):
        return self.parse_config("fog1", cloud_ip, cloud_port, fog2_ip, fog2_port)

    def get_fog2_config(self, cloud_ip, cloud_port):
        return self.parse_config("fog2", cloud_ip, cloud_port)

    """
        ### config format ###
        {
            ...,
            rules: {
                gps: [
                    {
                        data_type: ...,
                        name: ...,
                        modules: [...]
                    },
                    {
                        data_type: ...,
                        name: ...,
                        modules: [...]
                    },
                    ...
                ],
                traffic_camera: [...],
                ...
            }
        }
    """

    def parse_config(self, config_name, cloud_ip=None, cloud_port=None, fog2_ip=None, fog2_port=None,
                     folder_name="config"):
        cloud_url = utils.get_base_url(cloud_ip, cloud_port)
        fog2_url = utils.get_base_url(fog2_ip, fog2_port)

        config_folder_relative_path = folder_name + "/" + config_name

        with open(config_folder_relative_path + "/" + config_name + ".json", 'r') as f:
            config = json.load(f)

        config['rules'] = {}
        config_folder = os.path.join(self.project_root, config_folder_relative_path)
        rules_name = next(os.walk(config_folder))[1]
        for rule_name in rules_name:
            config['rules'][rule_name] = []
            rule_folder = os.path.join(config_folder, rule_name)
            rule_files_name = next(os.walk(rule_folder))[2]
            for rule_file_name in rule_files_name:
                with open(config_folder_relative_path + "/" + rule_name + "/" + rule_file_name, 'r') as f:
                    rule = json.load(f)

                    for module in rule['modules']:
                        if module.get('configs') is not None:
                            if module.get('configs').get('cloud_url') is not None and cloud_url is not None:
                                module.get('configs')['cloud_url'] = cloud_url
                            elif module.get('configs').get('fog2_url') is not None and fog2_url is not None:
                                module.get('configs')['fog2_url'] = fog2_url

                    config['rules'][rule_name].append(rule)

        return config

    def gen_and_request_update(self):
        self.gen_update()
        self.request_update()

    def gen_update(self):
        self.zip_modules()

        with open("node_meta3.json", 'r') as f:
            meta = json.load(f)

        meta["last_update_time"] = int(round(time.time() * 1000))
        self.last_update_time = meta["last_update_time"]

        with open('node_meta3.json', 'w') as f:
            json.dump(meta, f, indent=4)

        log.v(tag, "Updated last_update_time:", meta['last_update_time'])

    def zip_modules(self):
        modules_path = os.path.join(self.project_root, "modules")

        zipf = zipfile.ZipFile('modules.zip', 'w', zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(modules_path):
            for file in files:
                zipf.write(os.path.join(os.path.relpath(root, GlobalConfigs.instance().project_root), file))
        zipf.close()
        log.v(tag, "zipping modules done")

    def request_update(self):
        layers = self.nodes_ip.get("layers")

        for layer, layer_ips in layers.items():
            if layer != "cloud":
                for ip_port in layer_ips:
                    request_url = utils.get_base_url(ip_port['ip'], ip_port['port']) + "/request_update"
                    Network.instance().post(request_url)
