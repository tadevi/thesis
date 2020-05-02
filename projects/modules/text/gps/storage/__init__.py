# Storage GPS data to persistent storage
#
# This module should have def run(input, configs)
# @input: received data from protocols
# @configs: addition configs such as @database_name, @collection_name, @mongo_url
from modules.base import Base


class Main(Base):
    def __init__(self, configs):
        self.configs = configs

    def run(self, input):
        super(Main, self).run(input)
        # code below
