from typing import Dict

from modules.base import Filter
from modules import log, utils

tag = "Validate Air Record"


class Main(Filter):
    def __init__(self, configs):
        self.configs = configs

    def run(self, input: Dict):
        device_id = input.get("device_id")
        location = input.get("location")
        timestamp = input.get("timestamp")
        pm25 = input.get("pm25")

        result = False if (None in [device_id, location, timestamp, pm25] or
                           timestamp > utils.current_milli_time() or
                           not 0 < pm25 < 500) else True
        log.i(tag, "validated", result, "for input", input)
        return result
