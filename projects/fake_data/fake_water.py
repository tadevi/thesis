import random
import threading
import time
from modules.network import Network
from modules import utils
from modules.utils import log

tag = "WaterDataFaker"


class WaterDataFaker:
    def __init__(self, remote_url="http://35.187.225.56:3000", interval=5):
        self.network = Network({})
        self.is_canceled = False
        self.remote_url = remote_url
        self.interval = interval

    def start_posting_fake_data(self):
        t1 = threading.Thread(target=self.__post_fake_data)
        t1.start()

    def __post_fake_data(self):
        while not self.is_canceled:
            self.network.post(self.remote_url + '/iot/', self.__generate_fake_data())
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
