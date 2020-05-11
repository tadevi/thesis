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
DEFAULT_MONGO_COLLECTION = "test"

# mongo clients cache
mongo_clients = {}


class Main(Base):
    # configs should at least have "collection_name"
    def __init__(self, configs: Dict):
        self.configs = configs
        if "mongo_url" not in self.configs:
            self.configs["mongo_url"] = DEFAULT_MONGO_URL
        if "db_name" not in self.configs:
            self.configs["db_name"] = DEFAULT_MONGO_DB
        if "collection_name" not in self.configs:
            self.configs["collection_name"] = DEFAULT_MONGO_COLLECTION
        mongo_url = self.configs.get("mongo_url")
        self.mongo_client = mongo_clients.get(mongo_url)
        if self.mongo_client is None:
            self.mongo_client = pymongo.MongoClient(mongo_url)
            mongo_clients[mongo_url] = self.mongo_client
        db = self.mongo_client[self.configs["db_name"]]
        self.collection = db[self.configs["collection_name"]]

    def run(self, input: Dict):
        self.collection.insert_one(input)
        print("Storage: stored input ", input)
