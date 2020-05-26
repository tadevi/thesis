from typing import Dict

from modules.base import Filter
from modules.utils import log

tag = "Validate Water"


class Main(Filter):
    def __init__(self, configs):
        self.configs = configs

    def run(self, input: Dict):
        longitude = input.get("longitude")
        latitude = input.get("latitude")
        temperature = input.get("temperature")
        time = input.get("datetime")

        result = False if (None in [longitude, latitude, temperature, time] or
                           longitude < -180 or longitude > 180 or
                           latitude < -90 or latitude > 90) else True
        log.i(tag, "validated", result, "for input", input)
        return result
