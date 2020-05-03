# Storage GPS data to persistent storage
#
# This module should have def run(input, configs)
# @input: received data from protocols
# @configs: addition configs such as @database_name, @collection_name, @mongo_url
from modules.base import Base
from modules.text.gps.storage import StorageConfigs
import pymongo


class Main(Base):
    def __init__(self, configs: StorageConfigs):
        self.configs = configs

    def run(self, inputs):
        super(Main, self).run(inputs)
        # code below
        mongo_client = pymongo.MongoClient(self.configs.mongo_url)
        db = mongo_client[self.configs.db_name]
        collection = db[self.configs.collection_name]
        collection.insert_many(inputs)
