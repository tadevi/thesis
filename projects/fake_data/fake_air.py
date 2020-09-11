import random
import time
from threading import Thread

from modules import utils, log
from modules.network import Network

tag = "AirDataFaker"


class AirDataFaker:
    def __init__(self, district, remote_url="http://localhost:5000", interval=1):
        self.district = district
        self.is_canceled = False
        self.remote_url = remote_url
        self.interval = interval
        self.devices = self.create_devices()

    def create_devices(self):
        return [
            {
                'device_id': 'air-0',
                'location': 'Phuong 1 (long=10.855195, lat=106.741118)',
                'avg_pm25': 42
            },
            {
                'device_id': 'air-1',
                'location': 'Phuong 2 (long=10.814412, lat=106.707704)',
                'avg_pm25': 66.82
            },
            {
                'device_id': 'air-2',
                'location': 'Phuong 3 (long=10.777528, lat=106.700544)',
                'avg_pm25': 99
            },
            {
                'device_id': 'air-3',
                'location': 'Phuong 4 (long=10.769811, lat=106.724733)',
                'avg_pm25': 200
            },
            {
                'device_id': 'air-4',
                'location': 'Phuong 5 (long=10.760247, lat=106.661686)',
                'avg_pm25': 99
            },
            {
                'device_id': 'air-5',
                'location': 'Phuong 6 (long=10.725044, lat=106.630028)',
                'avg_pm25': 57.10
            },
            {
                'device_id': 'air-6',
                'location': 'Phuong 7 (long=10.763525, lat=106.656642)',
                'avg_pm25': 150
            },
            {
                'device_id': 'air-7',
                'location': 'Phuong 8 (long=10.811895, lat=106.649896)',
                'avg_pm25': 55.72
            },
            {
                'device_id': 'air-8',
                'location': 'Phuong 9 (long=10.886461, lat=106.598724)',
                'avg_pm25': 52.17
            },
            {
                'device_id': 'air-9',
                'location': 'Phuong 10 (long=10.679431, lat=106.704072)',
                'avg_pm25': 300
            },
        ]

    def start_posting_fake_data(self):
        Thread(target=self.__start_posting_fake_data_internal, daemon=True).start()

    def __start_posting_fake_data_internal(self):
        while not self.is_canceled:
            Network.instance().post(self.remote_url + '/iot/', self.__generate_fake_data(), threading=False)
            time.sleep(self.interval)
        log.v(tag, "stop posting data")

    def __generate_fake_data(self) -> dict:
        idx = random.randint(0, len(self.devices) - 1)
        device = self.devices[idx]
        avg = device['avg_pm25']
        half_range = 5
        pm25 = round((avg - half_range) + (random.random() * 2 * half_range), 2)

        return {
            "name": "air",
            "data": {
                'device_id': device['device_id'],
                'location': device['location'],
                'district': self.district,
                'timestamp': utils.current_milli_time(),
                'pm25': pm25
            }
        }
