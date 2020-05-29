# Storage GPS data to persistent storage
#
# This module should have def run(input, configs)
# @input: received data from server
# @configs: addition configs such as @database_name, @collection_name, @mongo_url
from typing import Dict

import requests
import traceback
import threading

from modules.utils import log

tag = "Network"

requests.adapters.DEFAULT_RETRIES = 2


class Network:
    # configs should at least have "collection_name"
    def __init__(self, configs: Dict):
        self.configs = configs

    def post(self, url, json):
        t = threading.Thread(target=self.__post, args=(url, json), daemon=True)
        t.start()

    def __post(self, url, json):
        try:
            response = requests.post(url, json=json)
            log.i(tag, "POST to url", url, "\nwith data", json, "\nstatus code:", response.status_code, "\nreason:",
                  response.reason)
            return {
                "status_code": response.status_code,
                "message": response.reason
            }
        except:
            traceback.print_exc()
            return {
                "status_code": -1,
                "message": "Exception"
            }

    def get(self, url, params=None) -> dict:
        try:
            response = requests.get(url, params=params)
            json = response.json()
            log.i(tag, "GET from url", url, "\nwith params:", params, "\nstatus code:", response.status_code, "\nreason:",
                  response.reason, "\njson:", json)
            return {
                "status_code": response.status_code,
                "message": response.reason,
                "data": json
            }
        except:
            traceback.print_exc()
            return {
                "status_code": -1,
                "message": "Exception"
            }
