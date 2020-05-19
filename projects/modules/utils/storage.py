# Storage GPS data to persistent storage
#
# This module should have def run(input, configs)
# @input: received data from protocols
# @configs: addition configs such as @database_name, @collection_name, @mongo_url
from typing import Dict

import pymongo

from modules.base import Base
from modules.utils import log

DEFAULT_MONGO_URL = "mongodb+srv://tai_than:tai_than123456@cluster0-osct2.mongodb.net/test?retryWrites=true&w=majority"
DEFAULT_MONGO_DB = "iot-db"
DEFAULT_MONGO_COLLECTION = "test"

# mongo clients cache
mongo_clients = {}

tag = "Storage"


class Main(Base):
    # configs should at least have "collection_name"
    def __init__(self, configs: Dict):
        self.configs = configs
        if self.configs.get("mongo_url") is None:
            self.configs["mongo_url"] = DEFAULT_MONGO_URL
        if self.configs.get("db_name") is None:
            self.configs["db_name"] = DEFAULT_MONGO_DB
        if self.configs.get("col_name") is None:
            self.configs["col_name"] = DEFAULT_MONGO_COLLECTION
        mongo_url = self.configs.get("mongo_url")
        self.mongo_client = mongo_clients.get(mongo_url)
        if self.mongo_client is None:
            self.mongo_client = pymongo.MongoClient(mongo_url)
            mongo_clients[mongo_url] = self.mongo_client
        self.db = self.mongo_client[self.configs["db_name"]]
        self.collection = self.db[self.configs["col_name"]]

    def run(self, input):
        try:
            if isinstance(input, list):
                if len(input) > 0:
                    self.collection.insert_many(input)
                else:
                    return
            else:
                self.collection.insert_one(input)
            log.i(tag, "stored input", input, "\nin mongo url:", self.configs['mongo_url'], ", db:",
                  self.configs['db_name'], ", collection:", self.configs['col_name'])
        except:
            pass

    def insert_one(self, collection, document):
        self.db[collection].insert_one(document)

    def insert_many(self, collection, documents):
        self.db[collection].insert_many(documents)

    def delete_one(self, collection, query):
        self.db[collection].delete_one(query)

    def delete_many(self, collection, query):
        self.db[collection].delete_many(query)

    def find_one(self, collection, query):
        return self.db[collection].find_one(query)

    def find_many(self, collection, query):
        return self.db[collection].find(query)
