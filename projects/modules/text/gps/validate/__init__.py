# Validate GPS data
# Remove unexpected value such as negative longtitude, lattitude, velocity
# Format data to the specified format to send to other modules
#
# This module should have def run(input, configs)
# @input: received data from protocols with json format.
# @configs: addition configs
# Using import json to decode json input to python dictionary
from datetime import datetime
from typing import Dict

from modules.base import Filter


class Main(Filter):
    def __init__(self, configs):
        self.configs = configs

    def run(self, input: Dict):
        super(Main, self).run(input)
        # code below
        result = False if (input["longitude"] < -180 or input["latitude"] > 180 or
                           input["latitude"] < -90 or input["latitude"] > 90 or
                           input["speed"] < 0) else True
        print("Validate GPS: validated ", str(result), " for input ", input)
        return result
