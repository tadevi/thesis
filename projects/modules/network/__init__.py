# Storage GPS data to persistent storage
#
# This module should have def run(input, configs)
# @input: received data from protocols
# @configs: addition configs such as @database_name, @collection_name, @mongo_url
from typing import Dict

import requests

from modules.base import Base

tag = "Network:"


class Main(Base):
    # configs should at least have "collection_name"
    def __init__(self, configs: Dict):
        self.configs = configs

    def post(self, url, json):
        response = requests.post(url, json=json)
        if response.status_code == 200:
            print(tag, "POST success to url", url, "\n with data", json)
        else:
            print(tag, "POST fail to url", url, "\nwith data", json, "status code:", response.status_code, ", reason:",
                  response.reason)
