from typing import Dict

from modules.base import Base
from modules.network import Network

tag = "Water to Cloud"


class Main(Base):
    def __init__(self, configs):
        self.configs = configs
        self.network = Network({})

    def run(self, input: Dict):
        self.network.post(self.configs['cloud_url'] + '/iot/', {
            "name": "water",
            "data": input
        })
