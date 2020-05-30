# Storage GPS data to persistent storage
#
# This module should have def run(input, configs)
# @input: received data from server
# @configs: addition configs such as @database_name, @collection_name, @mongo_url
import traceback
from typing import Dict

import requests

from modules.utils import log
from resource_manager.ThreadPool import ThreadPool
from resource_manager.ThreadTask import ThreadTask

tag = "Network"


class Network:
    # configs should at least have "collection_name"
    def __init__(self, configs: Dict):
        self.configs = configs

    def response_with(self, status, message, data=''):
        return {
            "status_code": status,
            "message": message,
            "data": data
        }

    def post(self, url, json):
        ThreadPool().get_thread().put_job(ThreadTask(self.__post, (url, json)))

    def __post(self, url, json):
        try:
            response = requests.post(url, json=json)
            log.i(tag, "POST to url", url, "\nwith data", json, "\nstatus code:", response.status_code, "\nreason:",
                  response.reason)

            return self.response_with(response.status_code, response.reason)
        except:
            log.e("Network", traceback.format_exc())
            return self.response_with(-1, "Something went wrong")

    def get(self, url, params=None) -> dict:
        try:
            response = requests.get(url, params=params)
            json = response.json()
            log.i(tag, "GET from url", url, "\nwith params:", params, "\nstatus code:", response.status_code,
                  "\nreason:",
                  response.reason, "\njson:", json)

            return self.response_with(response.status_code, response.reason, json)
        except:
            log.e("Network", traceback.format_exc())
            return self.response_with(-1, "Something went wrong")
