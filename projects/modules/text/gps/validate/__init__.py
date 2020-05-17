# Validate GPS data
# Remove unexpected value such as negative longtitude, lattitude, velocity
# Format data to the specified format to send to other modules
#
# This module should have def run(input, configs)
# @input: received data from server with json format.
# @configs: addition configs
# Using import json to decode json input to python dictionary
from typing import Dict

from modules.base import Filter
from modules.utils import log

tag = "Validate GPS"


class Main(Filter):
    def __init__(self, configs):
        self.configs = configs

    def run(self, input: Dict):
        longitude = input.get("longitude")
        latitude = input.get("latitude")
        speed = input.get("speed")
        time = input.get("datetime")

        result = False if (None in [longitude, latitude, speed, time] or
                           longitude < -180 or longitude > 180 or
                           latitude < -90 or latitude > 90 or
                           speed < 0) else True
        log.i(tag, "validated", result, "for input", input)
        return result
