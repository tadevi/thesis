# Validate GPS data
# Remove unexpected value such as negative longtitude, lattitude, velocity
# Format data to the specified format to send to other modules
#
# This module should have def run(input, configs)
# @input: received data from protocol_abstraction
# @configs: addition configs

from datetime import datetime
from typing import List
from projects.processing_module.text_processing.gps.GPSData import GPSData


def init(configs):
    pass


def run(inputs: List[GPSData], configs):
    for gpsData in inputs:
        if gpsData.longitude < -180 or gpsData.latitude > 180 or \
                gpsData.latitude < -90 or gpsData.latitude > 90 or \
                gpsData.speed < 0 or \
                gpsData.datetime > datetime.now():
            inputs.remove(gpsData)
    return inputs
