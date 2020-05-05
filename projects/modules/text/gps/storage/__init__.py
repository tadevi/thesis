# Storage GPS data to persistent storage
#
# This module should have def run(input, configs)
# @input: received data from protocols
# @configs: addition configs such as @database_name, @collection_name, @mongo_url
from typing import Dict

import pymongo

from modules.base import Base

DEFAULT_MONGO_URL = "mongodb+srv://tai_than:tai_than123456@cluster0-osct2.mongodb.net/test?retryWrites=true&w=majority"
DEFAULT_MONGO_DB = "iot-db"


class Main(Base):
    def __init__(self, configs: Dict):
        self.configs = configs
        if "mongo_url" not in self.configs:
            self.configs["mongo_url"] = DEFAULT_MONGO_URL
        if "db_name" not in self.configs:
            self.configs["db_name"] = DEFAULT_MONGO_DB

    def run(self, input: Dict):
        super(Main, self).run(input)
        # code below
        mongo_client = pymongo.MongoClient(self.configs["mongo_url"])
        db = mongo_client[self.configs["db_name"]]
        collection = db[self.configs["collection_name"]]
        collection.insert_one(input)
        print("Storage: stored input ", input)
