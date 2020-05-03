# Storage GPS data to persistent storage
#
# This module should have def run(input, configs)
# @input: received data from protocol_abstraction
# @configs: addition configs such as @database_name, @collection_name, @mongo_url
from typing import List

from projects.processing_module.text_processing.gps.GPSData import GPSData
from projects.processing_module.text_processing.gps.storage.StorageConfigs import StorageConfigs

import pymongo


def init(configs):
    pass


def run(inputs: list, configs: StorageConfigs):
    mongo_client = pymongo.MongoClient(configs.mongo_url)
    db = mongo_client[configs.db_name]
    collection = db[configs.collection_name]
    collection.insert_many(inputs)
    # for gps_data_dict in inputs:
    #     collection.insert_one(gps_data_dict)
