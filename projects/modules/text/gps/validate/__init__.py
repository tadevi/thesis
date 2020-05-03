# Validate GPS data
# Remove unexpected value such as negative longtitude, lattitude, velocity
# Format data to the specified format to send to other modules
#
# This module should have def run(input, configs)
# @input: received data from protocols with json format.
# @configs: addition configs
# Using import json to decode json input to python dictionary

from modules.base import Base
from datetime import datetime


class Main(Base):
    def __init__(self, configs):
        self.configs = configs

    def run(self, inputs):
        super(Main, self).run(inputs)
        # code below
        for gpsData in inputs:
            if gpsData.longitude < -180 or gpsData.latitude > 180 or \
                    gpsData.latitude < -90 or gpsData.latitude > 90 or \
                    gpsData.speed < 0 or \
                    gpsData.datetime > datetime.now():
                inputs.remove(gpsData)
        return inputs
