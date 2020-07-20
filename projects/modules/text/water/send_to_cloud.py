from typing import Dict

from modules.base import Base
from modules.network import Network

tag = "Water to Cloud"


class Main(Base):
    def __init__(self, configs):
        self.configs = configs

    def run(self, input: Dict):
        Network.instance().post(self.configs['cloud_url'] + '/iot/', {
            "name": "water",
            "data": input
        })
