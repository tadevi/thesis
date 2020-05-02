# Validate GPS data
# Remove unexpected value such as negative longtitude, lattitude, velocity
# Format data to the specified format to send to other modules
#
# This module should have def run(input, configs)
# @input: received data from protocols with json format.
# @configs: addition configs
# Using import json to decode json input to python dictionary

from modules.base import Base


class Main(Base):
    def __init__(self, configs):
        self.configs = configs

    def run(self, input):
        super(Main, self).run(input)
        # code below
