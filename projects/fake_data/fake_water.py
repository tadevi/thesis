import random
import time
from modules.network import Network
from modules import utils, log
from resource_manager.ThreadPool import ThreadPool
from resource_manager.ThreadTask import ThreadTask

tag = "WaterDataFaker"


class WaterDataFaker:
    def __init__(self, remote_url="http://35.187.225.56:3000", interval=5):
        self.is_canceled = False
        self.remote_url = remote_url
        self.interval = interval

    def start_posting_fake_data(self):
        ThreadPool.instance().get_thread().put_job(ThreadTask(self.__post_fake_data))

    def __post_fake_data(self):
        while not self.is_canceled:
            Network.instance().post(self.remote_url + '/iot/', self.__generate_fake_data())
            time.sleep(self.interval)
        log.v(tag, "stop posting data")

    def __generate_fake_data(self) -> dict:
        return {
            "name": "water",
            "data": {
                "longitude": random.uniform(-200, 200),
                "latitude": random.uniform(-100, 100),
                "temperature": random.normalvariate(28, 5),
                "datetime": utils.current_milli_time()
            }
        }
